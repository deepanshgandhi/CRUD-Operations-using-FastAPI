from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

engine=create_engine('sqlite:///students.db',echo=False)

Session=sessionmaker(bind=engine)
session=Session()

Base=declarative_base()

html="""<!DOCTYPE html>
<html>
<body>

<h2>HTML Forms</h2>

<form action="" onsubmit="sendMessage(event)">
  <label>Id:</label><br>
  <input type="text" id="Id" autocomplete="off"><br>
  <label>Name:</label><br>
  <input type="text" id="Name" autocomplete="off"><br>
  <label>Age:</label><br>
  <input type="text" id="Age" autocomplete="off"><br>
  <button>Send</button>
</form> 

<ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
            	var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
            	var input0 = document.getElementById("Id")
                var input1 = document.getElementById("Name")
                var input2 = document.getElementById("Age")
                var input=[]
                input[0]=input0.value
                input[1]=input1.value
                input[2]=input2.value
                ws.send(input)
                event.preventDefault()
            }
        </script>
</body>
</html>
"""
#https://fastapi.tiangolo.com/advanced/websockets/
class Student(Base):
	__tablename__='student'
	ide=Column(Integer, primary_key=True)
	name=Column(String(50))
	age=Column(Integer)

Base.metadata.create_all(engine)

app=FastAPI()

@app.get('/')
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
	await websocket.accept()
	while True:
		dat = await websocket.receive_text()
		data=dat.split(",")
		student=Student(ide=int(data[0]),name=data[1],age=int(data[2]))
		session.add(student)
		session.commit()
		students=session.query(Student)
		result=[]
		for student in students:
			res={}
			res["name"]=student.name
			res["age"]=student.age
			result.append(res)
		await websocket.send_text(f"Message text was: {result}")

@app.get('/getallstudents')
async def getAllStudents():
	students=session.query(Student)
	result=[]
	for student in students:
		res={}
		res["name"]=student.name
		res["age"]=student.age
		result.append(res)
	return result

@app.post('/addstudents')
async def addStudents(ide:int, name:str, age:int):
	student=Student(ide=ide,name=name,age=age)
	session.add(student)
	session.commit()
	return {"result":"successfully added"}

@app.put('/update')
async def updateRecords(age:int):
	student=session.query(Student).filter(Student.age<age).first()
	student.age=21
	session.commit()

@app.delete('/delete')
async def deleteRecords(age:int):
	student=session.query(Student).filter(Student.age==age).first()
	session.delete(student)
	session.commit()