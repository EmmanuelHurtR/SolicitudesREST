from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer,String


db=SQLAlchemy()
class Opcion(db.Model):
    __tablename__='opciones'
    idOpcion=db.Column(Integer,primary_key=True)
    nombre=db.Column(String,nullable=False)
    descripcion=db.Column(String)
    estatus=db.Column(String,default='A')

    def consultaGeneral(self):#select * from opciones
        lista=self.query.all()
        respuesta={"estatus":"","mensaje":""}
        try:
            if len(lista)>0:
                respuesta["estatus"]="OK"
                respuesta["mensaje"]="Listado de opciones de titulacion."
                respuesta["opciones"]=[o.to_json() for o in lista]
            else:
                respuesta["estatus"] = "OK"
                respuesta["mensaje"] = "No hay opciones registradas"
                respuesta["opciones"]=[]
        except:
            respuesta["estatus"] = "Error"
            respuesta["mensaje"] = "Problemas de al ejecutar la consulta de opciones"
        return respuesta

    def to_json(self):
        o_json={"idOpcion":self.idOpcion,
                "nombre":self.nombre,
                "descripcion":self.descripcion
        }
        return o_json

class Solicitud(db.Model):
    __tablename__='Solicitudes'
    idSolicitud=db.Column(Integer,primary_key=True)

    #Metodo que invoca el procedimienton almacenado sp_registrar_solicitud
    def agregar(self,json):
        respuesta={"estatus":"","mensaje":""}
        db.session.execute('call sp_registrar_solicitud(:tituloProyecto,:opcion,:alumno,@p_estatus,@p_mensaje)',json)
        db.session.commit()
        salida=db.session.execute('select @p_estatus,@p_mensaje').fetchone()
        respuesta['estatus']=salida[0]
        respuesta['mensaje'] = salida[1]
        return respuesta

    def editar(self,json):
        respuesta = {"estatus": "", "mensaje": ""}
        db.session.execute('call sp_modificar_solicitud(:idSolicitud,:tituloProyecto,:estatus,:opcion,:administrativo,:tipoUsuario,@p_estatus,@p_mensaje)', json)
        db.session.commit()
        salida = db.session.execute('select @p_estatus,@p_mensaje').fetchone()
        respuesta['estatus'] = salida[0]
        respuesta['mensaje'] = salida[1]
        return respuesta

    def eliminar(self,id):
        respuesta = {"estatus": "", "mensaje": ""}
        json={"idSolicitud":id}
        db.session.execute('call sp_eliminar_solicitud(:idSolicitud,@p_estatus,@p_mensaje)',json)
        db.session.commit()
        salida = db.session.execute('select @p_estatus,@p_mensaje').fetchone()
        respuesta['estatus'] = salida[0]
        respuesta['mensaje'] = salida[1]
        return respuesta

    def consultaGeneral(self):
        respuesta={"estatus":"","mensaje":"","solicitudes":""}
        resultado=db.session.execute("select * from vsolicitudes").fetchall()
        lista=[]
        for reg in resultado:
            lista.append(self.to_json(reg))
        if len(lista)>0:
            respuesta["estatus"]="OK"
            respuesta["mensaje"]="Listado de solicitudes"
            respuesta["solicitudes"]=lista
        else:
            respuesta["estatus"] = "OK"
            respuesta["mensaje"] = "No hay solicitudes registradas"
            respuesta["solicitudes"] = lista
        return respuesta

    def consultaIndividual(self,id):
        respuesta = {"estatus": "", "mensaje": ""}
        param={"id":id}
        resultado = db.session.execute("select * from vsolicitudes where idSolicitud=:id",param).fetchone()
        if resultado:
            respuesta["estatus"]="OK"
            respuesta["mensaje"]="Listado de la solicitud con id:"+str(id)
            respuesta["solicitud"]=self.to_json(resultado)
        else:
            respuesta["estatus"] = "OK"
            respuesta["mensaje"] = "No se encuentra registrada la solicitud con id:" + str(id)
        return respuesta

    def consultaSolicitudesAlumnos(self, id):
        respuesta = {"estatus": "", "mensaje": "", "solicitudes": ""}
        param = {"id": id}
        resultado = db.session.execute("select * from vsolicitudes where idAlumno=:id", param).fetchall()
        lista = []

        for reg in resultado:
            lista.append(self.to_json(reg))
        if len(lista) > 0:
            respuesta["estatus"] = "OK"
            respuesta["mensaje"] = "Listado de solicitudes del Alumno con ID: " + str(id)
            respuesta["solicitudes"] = lista
        else:
            respuesta["estatus"] = "OK"
            respuesta["mensaje"] = "No hay solicitudes registradas"
            respuesta["solicitudes"] = lista
        return respuesta

    def to_json(self,fila):
        solicitud={"administrativo":"","alumno":"","carrera":"","estatus":"","fechaAtencion":"",
                   "fechaRegistro":"","id":"","opcion":"","proyecto":""}
        solicitud["administrativo"]={"id":fila[10],"nombre":fila[11]}
        solicitud["alumno"]={"id":fila[1],"NC":fila[2],"nombre":fila[3]}
        solicitud["carrera"]={"id":fila[12],"nombre":fila[13]}
        solicitud["estatus"]=fila[7]
        solicitud["fechaAtencion"]=fila[6]
        solicitud["fechaRegistro"]=fila[5]
        solicitud["id"]=fila[0]
        solicitud["opcion"]={"id":fila[8],"nombre":fila[9]}
        solicitud["proyecto"]=fila[4]
        return solicitud
