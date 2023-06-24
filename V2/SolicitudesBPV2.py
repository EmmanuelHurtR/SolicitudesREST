from flask import Blueprint, request
from V2.model import Conexion
from flask_httpauth import HTTPBasicAuth

solicitudBPV2=Blueprint("solicitudBPV2", __name__)
auth=HTTPBasicAuth()

@auth.verify_password
def login(username, password):
    cn=Conexion()
    user=cn.validarCredenciales(username, password)
    if user!=None:
        return user
    else:
        return False

@auth.get_user_roles
def get_user_roles(user):
    return user["tipo"]

@auth.error_handler
def error_handler():
    return {"estatus":"Error", "mensaje":"No tiene autorizacion para realizar la ejecucion de la operacion"}

@solicitudBPV2.route('/Solicitudes/v2',methods=['POST'])
@auth.login_required(role='E')
def agregarSolicitud():
    cn=Conexion()
    datos=request.get_json()
    return cn.insertar_solicitud(datos)

@solicitudBPV2.route("/Solicitudes/v2", methods=['PUT'])
def modificarSolicitud():
    cn = Conexion()
    datos = request.get_json()
    return cn.modificar_solicitud(datos)

@solicitudBPV2.route('/Solicitudes/v2',methods=['GET'])
@auth.login_required(role=['A', 'E', 'D'])
def consultaSolicitudes():
    cn=Conexion()
    return cn.consultaGeneralSolicitudes()

@solicitudBPV2.route('/Solicitudes/v2/<string:id>',methods=['GET'])
@auth.login_required(role=['A', 'E', 'D'])
def consultarSolicitud(id):
    cn=Conexion()
    return cn.consultarSolicitud(id)

@solicitudBPV2.route('/Solicitudes/v2/<int:idAlumno>', methods=['GET'])
@auth.login_required(role=['A', 'E', 'D'])
def consultarSolicitudesAlumno(idAlumno):
    cn=Conexion()
    return cn.consultarSolicitudesAlumno(idAlumno)

@solicitudBPV2.route('/Solicitudes/v2/<string:id>', methods=['DELETE'])
@auth.login_required(role='E')
def eliminarSolicitud(id):
    cn=Conexion()
    return cn.eliminarSolicitud(id)