from flask import Blueprint, request
from V1.model import Solicitud

solicitudBP=Blueprint('SolicitudBP', __name__)

#Ruta para el listado general de solicitudes
@solicitudBP.route('/Solicitudes/v1',methods=['GET'])
def listadoSolicitudes():
    solicitud=Solicitud()
    return solicitud.consultaGeneral()

#Ruta para el listado indvidual de solicitudes en base al id de la solicitud
@solicitudBP.route('/Solicitudes/v1/<int:id>',methods=['GET'])
def listarSolicitud(id):
    solicitud=Solicitud()
    return solicitud.consultaIndividual(id)

#Ruta para agregar una solicitud
@solicitudBP.route('/Solicitudes/v1',methods=['POST'])
def agregarSolicitud():
    solicitud = Solicitud()
    data=request.get_json()
    return solicitud.agregar(data)

#Ruta para editar los datos de una solicitud
@solicitudBP.route('/Solicitudes/v1',methods=['PUT'])
def editarSolicitud():
    solicitud=Solicitud()
    data=request.get_json()
    return solicitud.editar(data)

#Ruta para eliminar una solicitud
@solicitudBP.route('/Solicitudes/v1/<int:id>',methods=['DELETE'])
def eliminarSolicitud(id):
    solicitud=Solicitud()
    return solicitud.eliminar(id)

#Ruta para consultar solicitudes de un alumno
@solicitudBP.route('/Solicitudes/Alumno/<int:id>',methods=['GET'])
def listarSolicitudAlumno(id):
    solicitud=Solicitud()
    return solicitud.consultaSolicitudesAlumnos(id)