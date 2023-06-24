from pymongo import MongoClient
from datetime import date, timedelta
from bson import ObjectId

class Conexion():
        def __init__(self):
            self.cliente=MongoClient()
            self.bd=self.cliente.titulaTECV3
            self.col=self.bd.solicitudes

        def insertar_solicitud(self, solicitud):
            respuesta = {"Estatus": "", "Mensaje": " "}
            # Proceso de validación de datos
            alumno = self.bd.usuarios.find_one(
                {"tipo": "E", "alumno.idAlumno": solicitud["idAlumno"], "alumno.estatus": "E", "estatus": "A"},
                projection={"alumno": True, "_id": False})
            if alumno:
                carrera = self.bd.carreras.find_one(
                    {"$and": [{"_id": alumno.get("alumno").get("carrera").get("idCarrera")},
                              {"planesEstudio": {
                                  "$elemMatch": {"clave": alumno.get("alumno").get("carrera").get("plan"),
                                                 "creditos": alumno.get("alumno").get("creditos")}}}]},
                    projection={"jefePrograma": True, "_id": False})

                if carrera:
                    count = self.col.count_document(
                        {"idAlumno": solicitud["idAlumno"], "estatus": {"$in": ["Captura", "Revision", "Autorizada"]}})
                    if count == 0:
                        count = self.bd.opciones.count_documents({"_id": solicitud["idOpcion"], "estatus": True,
                                                                  "carreras": {"$elemMatch": {
                                                                      "idCarrra": alumno.get("alumno").get(
                                                                          "carrera").get(
                                                                          "idCarrera"),
                                                                      "planes": {
                                                                          "$in": [alumno.get("alumno").get("plan")]}}}})
                        if count > 0:
                            solicitud["fechaRegistro"] = str(date.today())

                            suma = date.today() + timedelta(days=5)
                            solicitud["fechaAtencion"] = str(suma)
                            solicitud["estatus"] = "Captura"
                            solicitud["idAdministrativo"] = carrera["jefePrograma"]
                            self.col.insert_one(solicitud)
                            respuesta["Estatus"] = "OK"
                            respuesta["Mensaje"] = "Proyecto agregado con exito"
                        else:
                            respuesta["Estatus"] = "Error"
                            respuesta["Mensaje"] = "Opcion no encontrada"
                    else:
                        respuesta["Estatus"] = "Error"
                        respuesta["Mensaje"] = "El alumno ya tiene una solicitud en proceso o autorizada"
                else:
                    respuesta["Estatus"] = "Error"
                    respuesta["Mensaje"] = "No tiene los creditos suficiente de acuerdo a su plan de estudio"
            else:
                respuesta["Estatus"] = "Error"
                respuesta["Mensaje"] = "El usuario no existe"

            return respuesta

        def consultaGeneralSolicitudes(self):
            resp = {"estatus": "", "mensaje": ""}
            res = self.bd.vSolicitudes.find({})
            lista = []
            for s in res:
                self.to_json_solicitud(s)
                lista.append(s)
            if len(lista) > 0:
                resp["estatus"] = "OK"
                resp["mensaje"] = "listado de Solicitudes"
                resp["solicitudes"] = lista
            else:
                resp["estatus"] = "OK"
                resp["mensaje"] = "No hay Solicitudes registrado"
            return resp

        def consultarSolicitud(self, id):
            resp = {"estatus": "", "mensaje": ""}
            res = self.bd.vSolicitudes2.find_one({"id": ObjectId(id)})
            if res:
                self.to_json_solicitud(res)
                resp["estatus"] = "OK"
                resp["mensaje"] = "listado de la Solicitud"
                resp["solicitud"] = res
            else:
                resp["estatus"] = "OK"
                resp["mensaje"] = "No hay solicitudes registradas con ese id"
            return resp

        def consultarSolicitudesAlumno(self,idAlumno):
            resp={"estatus":"","mensaje":""}
            res=self.bd.solicitudes.find({"alumno.id":idAlumno})
            lista=[]
            for s in res:
                self.to_json_solicitud(s)
                lista.append(s)
            if len(lista)>0:
                resp["estatus"] = "OK"
                resp["mensaje"] = "Listado de solicitudes del alumno"
            else:
                resp["estatus"]="OK"
                resp["mensaje"]="El alumno no tiene solicitudes registradas"
            return resp

        def eliminarSolicitud(self,id):
            resp={"estatus":"","mensaje":""}
            res=self.bd.solicitudes.delete_one({"_id":ObjectId(id), "estatus":{"$in":["Captura","Rechazada"]}})
            if res.delete_count>0:
                resp["estatus"]="OK"
                resp["mensaje"]="La solicitud se elimino con exito"
            else:
                resp["estatus"] = "Error"
                resp["mensaje"] = "La solicitud no existe o no se encuentra en Captura/Rechazada"
            return resp

        def modificar_solicitud(self, data):
            resp = {"estatus:": "", "mensaje:": ""}
            res = self.bd.solicitudes.find_one({"_id": data["idSolicitud"]})
            opcion = self.bd.opciones.find_one({"_id": data["opcion"]})
            if res:
                if data["tipoUsuario"] == "E":
                    if res.get("estatus") == "Captura":
                        opcion = self.bd.opciones.find_one({"_id": data["opcion"]})
                        if "tituloProyecto" in data and "opcion" in data:
                            if data["tituloProyecto"] != "":
                                res["proyecto"] = data["tituloProyecto"]
                            if opcion and opcion["estatus"]:
                                res["idOpcion"] = data["opcion"]
                                res["fechaAtencion"] = str(date.today())
                                self.bd.solictudes.update_one({"_id": data["idSolicitud"]}, {"$set": res})
                                resp["estatus:"] = "OK"
                                resp["mensaje:"] = "Se actualizo correctamente"
                            else:
                                resp["estatus:"] = "Error"
                                resp["mensaje:"] = "La opcion no se enceuntra o no esta disponible"
                        else:
                            resp["estatus:"] = "Error"
                            resp["mensaje:"] = "No se registro la opcion o el titulo para actualizar"
                    else:
                        resp["estatus:"] = "Error"
                        resp["mensaje:"] = "No se puede actualizar, verifica que la solicitud se encuentre en estado de Captura"

                elif "A" == data["tipoUsuario"]:
                    if res.get("estatus") == "Captura" or res.get("estatus") == "Revision":
                        admi = self.bd.usuarios.find_one({"_id": data["administrativo"]})
                        actEst = ""
                        if data["estatus"] == "Revsión" or data["estatus"] == "Rechazada" or data[
                            "estatus"] == "Captura" or data["estatus"] == "Autorizada":
                            res["estatus"] = data["estatus"]
                        else:
                            actEst = "No se pudo actualizar el estatus porque ingresaste un estatus invalido "
                        if admi and admi["estatus"] == "A":
                            res["idAdministrativo"] = data["administrativo"]
                            res["fechaAtencion"] = str(date.today())
                            self.bd.solicitudes.update_one({"_id": data["idSolicitud"]}, {"$set": res})
                            resp["estatus:"] = "Ok"
                            resp["mensaje:"] = "Se actualizo la solicitud "
                        else:
                            resp["estatus:"] = "Error"
                            resp["mensaje:"] = "No existe el administrativo"
                    else:
                        resp["estatus:"] = "Error"
                        resp["mensaje:"] = "La solicitud no se puede actualizar porque no esta en estatus Captura/Revision"
                else:
                    resp["estatus:"] = "Error"
                    resp["mensaje:"] = "No registraste un tipo de usuario valido"
            else:
                resp["estatus:"] = "Error"
                resp["mensaje:"] = "La solicitud no existe"
            return resp

        def validarCredenciales(self, usuario, password):
            user=self.bd.usuarios.find_one({"email":usuario, "password":password, "estatus":"A"})
            if user:
                return user
            else:
                return None

        def to_json_solicitud(self, solicitud):
            solicitud["administrativo"] = {"id": solicitud.get("administrativo")[0].get("id"),
                                           "nombre": solicitud.get("administrativo")[0].get("nombre")[0]}
            solicitud["alumno"] = {"id": solicitud.get("alumno")[0].get("id"),
                                   "NC": solicitud.get("alumno")[0].get("NC")[0],
                                   "nombre": solicitud.get("alumno")[0].get("nombre")[0]}
            solicitud["carrera"] = {"id": solicitud.get("carrera")[0].get("id")[0],
                                    "nombre": solicitud.get("carrera")[0].get("nombre")[0]}
            solicitud["opcion"] = {"id": solicitud.get("opcion")[0].get("id"),
                                   "nombre": solicitud.get("opcion")[0].get("nombre")[0]}
            solicitud["id"] = str(solicitud["id"])