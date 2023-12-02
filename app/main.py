import os
import secrets

from common_types import ConfigType, FileValidationResult
import validator

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import tempfile

from datetime import datetime as dt

__version__ = 'demo'
__start__ = dt.now()

#
# Credential checking
#

if os.getenv('SERVICE_AUTH_USERNAME'):
    basic_auth_username: str = os.getenv('SERVICE_AUTH_USERNAME')
    basic_auth_password: str = os.getenv('SERVICE_AUTH_PASSWORD')
else:
    basic_auth_username: str = 'my_user'
    basic_auth_password: str = 'my_pass'


basic_auth = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(basic_auth)):
    correct_username = secrets.compare_digest(credentials.username, basic_auth_username)
    correct_password = secrets.compare_digest(credentials.password, basic_auth_password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


#
# Service
#

app = FastAPI()


@app.get('/')
def index():
    return {'version': __version__,
            'start_time': __start__,
            'now': dt.now()}


@app.post('/validate_file', response_model=FileValidationResult)
async def validate_file(config_type: ConfigType,
                        file: UploadFile = File(),
                        # credentials: HTTPBasicCredentials = Depends(get_current_username)
                        ):

    _, file_extension = os.path.splitext(file.filename)

    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as _file:
        _content = await file.read()
        _file.write(_content)
        _tmp_file_name = _file.name

    res = validator.run_test(_tmp_file_name, config_type)
    res.file_name = file.filename
    res.version = __version__

    os.remove(_tmp_file_name)

    return res

#
# Debug
#

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app="main:app", port=8000)
