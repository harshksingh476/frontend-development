from flask import Blueprint, request, jsonify, render_template, url_for, current_app, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from repos.modules import Task, Document, Project
from sqlalchemy import or_
import os
from datetime import datetime
from repos import db
from repos.users.routes import logout


aavana = Blueprint('aavana', __name__)


@aavana.route('/aavana_home', methods=['POST', 'GET'])
@login_required
def aavana_home():
    print(Task.query.all()[0].task_id)
    if not current_user.is_authenticated or 'PROJECT_IDS' not in session:
        pass
        # logout()



    if request.method == 'POST':
        all_tasks_results = Task.query.all()
        mainTableDataList = []
        headers = ["UID","Entity Name","Location Code","Type of License","State","District","Locality","Project_ID","Assigned Date","License Expiry Date", "Status", "Document Status", "Comment","",""]
        mainTableDataList.append(headers)
        for row in all_tasks_results:
            rowLevelData=[]
            task_id = row.task_id
            document_name = Document.query.filter(Document.task_id == task_id, Document.file_status == 0).all()
            project_name = Project.query.with_entities(Project.project_name).filter_by(id=row.project_id).first()[0]
            entity_name = row.entity_name
            location_code = row.location_code
            type_of_license = row.type_of_licence
            state = row.state
            district = row.district
            locality = row.locality
            project_id = row.project_id
            assigned_date = row.created_time.strftime('%d/%m/%Y') if row.created_time is not None else ''
            licence_expiry_date = row.licence_expiry_date.strftime('%d/%m/%Y') if row.licence_expiry_date is not None else ''

            status = row.status
            if document_name:
                document_status = "Completed"
            else:
                document_status = "Pending"
            comment = ""

            rowLevelData.append(task_id)
            rowLevelData.append(entity_name)
            rowLevelData.append(location_code)
            rowLevelData.append(type_of_license)
            rowLevelData.append(state)
            rowLevelData.append(district)
            rowLevelData.append(locality)
            rowLevelData.append(project_id)
            rowLevelData.append(assigned_date)
            rowLevelData.append(licence_expiry_date)
            rowLevelData.append(status)
            rowLevelData.append(document_status)
            rowLevelData.append(comment)
            rowLevelData.append("")
            rowLevelData.append("")

            mainTableDataList.append(rowLevelData)

        print(mainTableDataList)
        
        response = {
                'dataArray': mainTableDataList,
            }
        
        
        return jsonify(response)

    return render_template('aavana_home_v2.html')


@aavana.route('/upload', methods=['POST'])
def upload_file():
    try:
        try:
            if 'file' not in request.files:
                return jsonify({"error": "No file part"}), 400

            file = request.files['file']
            task_id = request.form['task_id']
            project_id = request.form['project_id']
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400

            document_data = {}
            document_data['task_id'] = task_id
            UPLOAD_FOLDER = current_app.config.get('UPLOAD_FOLDER')
            project_name = Project.query.with_entities(Project.project_name).filter_by(id=project_id).first()[0]
            document_data['project_name'] = project_name
            project_dir = os.path.join(UPLOAD_FOLDER, project_name)
            os.makedirs(project_dir, exist_ok=True)
            task_dir = os.path.join(project_dir, task_id)
            os.makedirs(task_dir, exist_ok=True)
            filename = secure_filename(file.filename)
            document_data['filename'] = file.filename
            file_path = os.path.join(task_dir, filename)
            document_data['file_path'] = file_path[5:]

            file.save(file_path)

            document_info = Document(file_name=filename, task_id=task_id)
            db.session.add(document_info)
            db.session.flush()
            db.session.commit()

            saved_document_id = document_info.id
            document_data['saved_document_id'] = saved_document_id
            document_data['message'] = "File uploaded successfully"
            return jsonify(document_data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        return jsonify({"message": "File uploaded successfully"}), 200
    except Exception as e:
        return f'Error: {str(e)}'


@aavana.route('/delete_document', methods=['POST'])
def delete_document():
    document_to_update = Document.query.get(request.form['docId'])

    if document_to_update:
        # Update the file_status
        document_to_update.file_status = 1

        # Commit the changes to the database
        db.session.commit()

        # Optionally, you can return a response indicating success
        response = {"message": "File status updated successfully"}
    else:
        # Handle the case where the document with the given ID does not exist
        response = {"error": "Document not found"}

    return jsonify(response)

