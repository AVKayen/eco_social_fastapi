from pydantic import BaseModel


class ResponseModel(BaseModel):
    status: str

    @staticmethod
    def success():
        return ResponseModel(status='Success')

    @staticmethod
    def error():
        return ResponseModel(status='Something went wrong')
