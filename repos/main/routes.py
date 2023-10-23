from flask import Blueprint, request, jsonify, render_template, url_for, session, redirect
from sqlalchemy import or_
from flask_login import login_required, current_user
from repos.modules import Task, Document, Project
from repos.users.routes import logout

main = Blueprint('main', __name__)


@main.route('/home', methods=['POST', 'GET'])
@login_required
def home():
    if not current_user.is_authenticated or 'PROJECT_IDS' not in session:
        logout()

    company_name = current_user.project_name
    project_ids = session.get('PROJECT_IDS')
    project_filter = [Task.project_id == project_id for project_id in project_ids]
    project_id_filter = or_(*project_filter)
    if request.method == 'POST':
        draw = request.form['draw']
        row = int(request.form['start'])
        row_per_page = int(request.form['length'])
        searchValue = request.form["search[value]"]
        column_search = {}
        # if searchValue:
        #     column_search['task_id'] = searchValue
        column1_search = request.form.get('columns[0][search][value]')
        if column1_search:
            column_search['entity_name'] = column1_search
        column2_search = request.form.get('columns[1][search][value]')
        if column2_search:
            column_search['location_code'] = column2_search
        column3_search = request.form.get('columns[2][search][value]')
        if column3_search:
            column_search['type_of_licence'] = column3_search
        column4_search = request.form.get('columns[3][search][value]')
        if column4_search:
            column_search['state'] = column4_search
        column5_search = request.form.get('columns[4][search][value]')
        if column5_search:
            column_search['district'] = column5_search
        column6_search = request.form.get('columns[5][search][value]')
        if column6_search:
            column_search['locality'] = column6_search
        column7_search = request.form.get('columns[6][search][value]')
        if column7_search:
            column_search['created_time'] = column7_search
        column8_search = request.form.get('columns[7][search][value]')
        if column8_search:
            column_search['licence_expiry_date'] = column8_search
        column9_search = request.form.get('columns[8][search][value]')
        if column9_search:
            column_search['status'] = column9_search

        # total number of count without filtering
        total_task_count = Task.query.filter(project_id_filter).count()

        like_string = '%{}%'.format(searchValue)
        # with filtering query
        filter_query = Task.query.filter(project_id_filter, or_(Task.entity_name.ilike(like_string),
                                                                Task.client_status.ilike(like_string),
                                                                Task.state.ilike(like_string),
                                                                Task.district.ilike(like_string),
                                                                Task.type_of_licence.ilike(like_string),
                                                                Task.location_code.ilike(like_string),
                                                                Task.created_time.ilike(like_string),
                                                                Task.licence_expiry_date.ilike(like_string),
                                                                Task.locality.ilike(like_string)))

        # total number of count with filtering
        total_recordwith_filter_count = filter_query.count()
        filter_result = filter_query.all()

        # Column-wise filter
        or_conditions = []
        if bool(column_search):
            for column_name, column_search_value in column_search.items():
                filter_condition = getattr(Task, column_name).ilike(f'%{column_search_value}%')
                or_conditions.append(filter_condition)

            filter_column = Task.query.filter(project_id_filter, or_(*or_conditions))
            filter_column_result = filter_column.all()

        task_data = []
        if searchValue != '':
            tasks = filter_query.offset(row).limit(row_per_page).all()
            if bool(column_search):
                # Extract the attribute that you want to use for comparison, for example 'task_id'
                task_ids = [task.task_id for task in filter_result]
                filter_task_ids = [task.task_id for task in filter_column_result]

                # Find common task_ids between the two lists
                common_task_ids = list(set(task_ids) & set(filter_task_ids))

                # Filter the original lists to get the common objects
                common_tasks = [task for task in filter_result if task.task_id in common_task_ids]
                total_recordwith_filter_count = len(common_tasks)
                tasks = common_tasks[row:row + row_per_page]
        elif bool(column_search):
            tasks = filter_column.offset(row).limit(row_per_page).all()
            # Extract the attribute that you want to use for comparison, for example 'task_id'
            task_ids = [task.task_id for task in filter_result]
            filter_task_ids = [task.task_id for task in filter_column_result]

            # Find common task_ids between the two lists
            common_task_ids = list(set(task_ids) & set(filter_task_ids))

            # Filter the original lists to get the common objects
            common_tasks = [task for task in filter_result if task.task_id in common_task_ids]
            total_recordwith_filter_count = len(common_tasks)
        else:
            tasks = Task.query.filter(project_id_filter).offset(row).limit(row_per_page).all()

        for row in tasks:
            document_name = Document.query.filter(Document.task_id == row.task_id, Document.file_status == 0).all()
            project_name = Project.query.with_entities(Project.project_name).filter_by(id=row.project_id).first()[0]
            cols = ''
            if document_name:
                for doc in document_name:
                    cols += f'<div class="button-container">' + \
                            '<div class="button-group">' + \
                            f'<a href="' + url_for('static', filename='imageupload/' + project_name + '/' + str(
                        row.task_id) + '/' + doc.file_name) + '" class="btn-sm btn-smaller btn-download" ' \
                                                              'target="_blank">' + doc.file_name + '</a>' '</div>''</div>'
            else:
                cols += '<p><span style="color: orange;">Proccesing</span></p>'

            created_time = row.created_time.strftime('%d/%m/%Y') if row.created_time is not None else ''
            licence_expiry_date = row.licence_expiry_date.strftime(
                '%d/%m/%Y') if row.licence_expiry_date is not None else ''

            task_data.append({
                'document': cols,
                'task_id': f'{row.task_id}',
                'entity_name': row.entity_name,
                'status': row.client_status,
                'state': row.state,
                'district': row.district,
                'type_of_licence': row.type_of_licence,
                'location_code': row.location_code,
                'assigned_date': created_time,
                'licence_expiry_date': licence_expiry_date,
                'locality': row.locality,
            })

        response = {
            'draw': draw,
            'iTotalRecords': total_task_count,
            'iTotalDisplayRecords': total_recordwith_filter_count,
            'aaData': task_data,
        }
        return jsonify(response)
    else:
        tasks_status = Task.query.filter(project_id_filter).all()
        start = len(tasks_status)
        doc_pending, under_process, onhold, closed = 0, 0, 0, 0
        for status_value in tasks_status:
            if status_value.client_status == 'Document Pending':
                doc_pending += 1
            elif status_value.client_status == 'On Hold':
                onhold += 1
            elif status_value.client_status == 'Closed':
                closed += 1
            else:
                under_process += 1

        status_count = (
            {'start_count': start, 'doc_pending_count': doc_pending, 'under_process_count': under_process,
             'onhold_count': onhold, 'closed_count': closed})

        return render_template('home.html', status_count=status_count, project_name=company_name)


@main.route('/task_status_data', methods=['POST', 'GET'])
@login_required
def task_status_data():
    if 'PROJECT_IDS' not in session:
        return redirect(url_for('users.login'))

    company_name = current_user.project_name
    project_ids = session.get('PROJECT_IDS')
    project_filter = [Task.project_id == project_id for project_id in project_ids]
    project_id_filter = or_(*project_filter)
    if request.method == 'POST':
        filter_status = request.form["status"]
        draw = request.form['draw']
        row = int(request.form['start'])
        row_per_page = int(request.form['length'])
        searchValue = request.form["search[value]"]

        # total number of count without filtering
        client_status_condition = Task.client_status == filter_status
        total_task_count = Task.query.filter(project_id_filter, client_status_condition).count()

        like_string = '%{}%'.format(searchValue)
        # with filtering query
        if filter_status == 'assigned':
            filter_query = Task.query.filter(project_id_filter,
                                             or_(Task.entity_name.ilike(like_string),
                                                 Task.client_status.ilike(like_string),
                                                 Task.state.ilike(like_string),
                                                 Task.district.ilike(like_string),
                                                 Task.type_of_licence.ilike(like_string),
                                                 Task.location_code.ilike(like_string),
                                                 Task.created_time.ilike(like_string),
                                                 Task.licence_expiry_date.ilike(like_string),
                                                 Task.locality.ilike(like_string)))
        else:
            filter_query = Task.query.filter(project_id_filter, Task.client_status == filter_status,
                                             or_(Task.entity_name.ilike(like_string),
                                                 Task.client_status.ilike(like_string),
                                                 Task.state.ilike(like_string),
                                                 Task.district.ilike(like_string),
                                                 Task.type_of_licence.ilike(like_string),
                                                 Task.location_code.ilike(like_string),
                                                 Task.created_time.ilike(like_string),
                                                 Task.licence_expiry_date.ilike(like_string),
                                                 Task.locality.ilike(like_string)))

        # total number of count with filtering
        total_recordwith_filter_count = filter_query.count()

        task_data = []
        if searchValue == '':
            if filter_status == 'assigned':
                tasks = Task.query.filter(project_id_filter).offset(row).limit(
                    row_per_page).all()
            else:
                tasks = Task.query.filter(project_id_filter, Task.client_status==filter_status).offset(row).limit(
                        row_per_page).all()
        else:
            tasks = filter_query.all()

        for row in tasks:
            document_name = Document.query.filter(Document.task_id == row.task_id, Document.file_status == 0).all()
            cols = ''
            if document_name:
                for doc in document_name:
                    cols += f'<div class="button-container">' + \
                            '<div class="button-group">' + \
                            f'<a href="' + url_for('static', filename='imageupload/' + company_name + '/' + str(
                        row.task_id) + '/' + doc.file_name) + '" class="btn-sm btn-smaller btn-download" ' \
                                                              'target="_blank">' + doc.file_name + '</a>' '</div>''</div>'
            else:
                cols += '<p><span style="color: orange;">Proccesing</span></p>'

            created_time = row.created_time.strftime('%d/%m/%Y') if row.created_time is not None else ''
            licence_expiry_date = row.licence_expiry_date.strftime(
                '%d/%m/%Y') if row.licence_expiry_date is not None else ''

            task_data.append({
                'document': cols,
                'task_id': f'{row.task_id}',
                'entity_name': row.entity_name,
                'status': row.client_status,
                'state': row.state,
                'district': row.district,
                'type_of_licence': row.type_of_licence,
                'location_code': row.location_code,
                'assigned_date': created_time,
                'licence_expiry_date': licence_expiry_date,
                'locality': row.locality,
            })

        response = {
            'draw': draw,
            'iTotalRecords': total_task_count,
            'iTotalDisplayRecords': total_recordwith_filter_count,
            'aaData': task_data,
        }
        return jsonify(response)
