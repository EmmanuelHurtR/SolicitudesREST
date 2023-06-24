from flask import Flask,jsonify,request
from V1.model import Opcion,db,Solicitud
from V1.SolicitudesBPV1 import solicitudBP
from V2.SolicitudesBPV2 import solicitudBPV2

app=Flask(__name__)
app.register_blueprint(solicitudBP) #Cargar la funcionalidad inclueda en el componente solicitudBP
app.register_blueprint(solicitudBPV2) #Cargar la funcionalidad inclueda en el componente solicitudBPV2
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://titulatec_soa:Hola.123@localhost/TitulaTEC_SOA'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

@app.route('/',methods=['GET'])
def init():
    return {"mensaje":"Escuchando el Servicio REST de Solicitudes"}

#Ruta para el listado de las opciones disponibles para titulación
@app.route('/opciones',methods=['GET'])
def consultaOpciones():
    try:
        opcion=Opcion()
        return jsonify(opcion.consultaGeneral())
    except:
        respuesta = {"estatus": "Error", "mensaje": "Recurso no disponible, contacta al administrador del servicio"}
        return respuesta

#Manipulaciones de errores
@app.errorhandler(404)
def errorinterno(e):
    respuesta={"estatus":"Error","mensaje":"Recurso no disponible, contacta al administrador del servicio"}
    return respuesta

if __name__=='__main__':
    db.init_app(app)
    app.run(debug=True)