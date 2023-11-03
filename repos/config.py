
class Config:
    SECRET_KEY = 'kdsfjsddfskmsdkmdkmsfmksdlfmds'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:''@localhost/repos2'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'repos/static/imageupload/'