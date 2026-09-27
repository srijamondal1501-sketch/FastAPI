from fastapi import FastAPI,Path,HTTPException,Query
from json import load,dump
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal,Optional
app = FastAPI()

class Patient(BaseModel):
    id:Annotated[str,Field(...,description='ID of the Ptient',examples=['P001'])]
    name:Annotated[str,Field(...,description="Name Of The Patient")]
    city:Annotated[str,Field(...,description="City Where The Patient Is Living")]
    age:Annotated[int,Field(...,description="Age Of The Patient",gt=0,lt=120)]
    gender:Annotated[Literal['male','female','others'],Field(...,description="Choose Your Gender")]
    height:Annotated[float,Field(...,gt=0,description="Height Of The Patient in meters")]
    weight:Annotated[float,Field(...,gt=0,description="Weight Of The Patient kgs")]
    @computed_field
    @property
    def bmi(self)-> float:
        bmi=round(self.weight/(self.height**2),2)
        return bmi
    @computed_field
    @property
    def verdict(self)->str:
        if self.bmi<18.5:
            return 'underweight'
        elif self.bmi<25:
            return 'Normal'
        elif self.bmi<30:
            return 'Normal'
        else:
            return "obese"   
class PatientUpdate(BaseModel):
    name:Annotated[Optional[str],Field(default=None)]
    city:Annotated[Optional[str],Field(default=None)]
    age:Annotated[Optional[int],Field(default=None)]
    gender:Annotated[Optional[Literal['male','female']],Field(default=None)]
    height:Annotated[Optional[float],Field(default=None,gt=0)]
    weight:Annotated[Optional[float],Field(default=None,gt=0)]  




@app.get("/")
def hello():
    return {"message": "Patient Management System API"}

@app.get("/about")
def about():
    return {"message": "A Fully Functional API For Managing Details Of Patient"}  
@app.get("/load_data")
def load_data():
    with open("dataset.json","r") as file:
        data=load(file)
    return data
def save_data(data):
    with open('dataset.json','w') as f:
        dump(data,f)


@app.get("/view")
def view():
    data=load_data()
    return data
@app.get("/patient/{patient_id}") 
def view_patient(patient_id: str=Path(...,description='Id of the Patient',examples='P001')):
    data=load_data()
    if patient_id in data:
        return {'message':data[patient_id]}
    else:
        raise HTTPException(status_code=404,detail='Patient not found')
@app.get('/sort')
def sort_patient(sort_by:str =Query(...,description='Sort on the basis of height,weight or bmi'),order:str =Query('asc',description='sort in asc or desc order')) :
    valid_field=['height','weight','bmi']
    if sort_by not in valid_field:
        raise HTTPException(status_code=400,detail='Invalid field')
    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail='Invalid order field')  
    data=load_data()
    sorted_data=sorted(data.items(),key=lambda x: x[1][sort_by],reverse=(order=="desc"))
    return dict(sorted_data) 
@app.post('/create') 
def create_patient(patient:Patient):
    data=load_data()
    if patient.id in data:
        raise HTTPException(status_code=400,detail='Patient already exists')    
    data[patient.id]=patient.model_dump(exclude=['id']) 
    save_data(data) 
    return JSONResponse(status_code=201,content={'message':'patient created successfully'}) 
@app.put('/edit/{patient_id}')
def update_patient(patient_id:str,patient_update=PatientUpdate):
    data=load_data()
    if patient_id in data:
        raise HTTPException(status_code=404,detail='Patient not found')
    existing_patient_info=data[patient_id]
    updated_patient_info=patient_update.model_dump(exclude_unset=True)    
    for key,value in updated_patient_info.items():
        existing_patient_info[key]=value
    #existing_patient_info-> pydantic object - > updated bmi + verdict -> pydantic object ->dict  #
    existing_patient_info['id']=patient_id
    patient_pydantic_obj=Patient(**existing_patient_info)
    existing_patient_info=patient_pydantic_obj.model_dump(exclude='id')
    data[patient_id]=existing_patient_info
    save_data(data)
    return JSONResponse(status_code=200,content={'message:patient updated'})   





         



       



