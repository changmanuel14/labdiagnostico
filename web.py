from flask import Flask, render_template, url_for, flash, redirect, request, Response, session, send_from_directory, make_response
import os
from os import path, getcwd
import pymysql
from datetime import date, datetime
import pdfkit
from operator import attrgetter
from PIL import Image
from fpdf import FPDF
from conexion import Conhost, Conuser, Conpassword, Condb

app = Flask(__name__)
app.secret_key = 'd589d3d0d15d764ed0a98ff5a37af547'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

mi_string = chr(92)
PATH_FILE = getcwd() + f'{mi_string}static{mi_string}documentos{mi_string}'

@app.route("/login", methods=['GET', 'POST'])
def login():
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
		return redirect(url_for('inicio'))
	except:
		logeado = 0
		idtipouser = 0
	if request.method == 'POST':
		user = request.form["user"]
		pwd = request.form["pwd"]
		try:
			conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
			try:
				with conexion.cursor() as cursor:
					consulta = "SELECT idusers, nombre, idtipouser FROM users WHERE user = %s and pwd = md5(%s)"
					cursor.execute(consulta, (user, pwd))
					data = cursor.fetchall()
					if len(data) == 0:
						return render_template('login.html', title='Iniciar sesión', logeado=logeado, idtipouser = idtipouser, mensaje="Datos inválidos, intente nuevamente")
					else:
						session['logeadoldd'] = 1
						session['iduserldd'] = data[0][0]
						session['nombreuserldd'] = data[0][1]
						session['idtipouserldd'] = data[0][2]
						session['userldd'] = user
						return redirect(url_for('inicio'))
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
	return render_template('login.html', title='Iniciar sesión', logeado=logeado, idtipouser = idtipouser, mensaje="")

@app.route("/logout")
def logout():
	session.pop('logeadoldd', None)
	session.pop('nombreuserldd', None)
	session.pop('userldd', None)
	session.pop('iduserldd', None)
	session.pop('idtipouserldd', None)
	return redirect(url_for('inicio'))

@app.route("/crearusuario", methods=['GET', 'POST'])
def crearusuario():
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
		return redirect(url_for('login'))

	try:
		conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
		try:
			with conexion.cursor() as cursor:
				consulta = "SELECT idtipouser, tipouser FROM tipouser;"
				cursor.execute(consulta)
				tyuser = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)

	if request.method == 'POST':
		nombre = request.form["nombre"]
		user = request.form["user"]
		pwd = request.form["pwd"]
		tipouser = request.form["tipouser"]
		try:
			conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
			try:
				with conexion.cursor() as cursor:
					consulta = "INSERT INTO users(nombre, user, pwd, idtipouser) values (%s, %s, MD5(%s), %s);"
					cursor.execute(consulta, (nombre, user, pwd, tipouser))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('inicio'))
	return render_template('crearusuario.html', title='Nuevo Usuario', logeado=logeado, idtipouser = idtipouser, tipos = tyuser)

@app.route("/")
def inicio():
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
		try:
			with conexion.cursor() as cursor:
				cursor.execute("SELECT i.codigo, i.nombre, i.presentacion, t.tipo, i.existencia from insumos i inner join tipo t ON i.idtipo = t.idtipo where i.activo = 1  order by t.tipo asc, codigo asc;")
			# Con fetchall traemos todas las filas
				insumos = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('inicio.html', title='Inicio', insumos = insumos, logeado=logeado, idtipouser = idtipouser)

@app.route("/nuevoinsumo", methods=['GET', 'POST'])
def nuevoinsumo():
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
		return redirect(url_for('login'))
	try:
		conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
		try:
			with conexion.cursor() as cursor:
				cursor.execute("SELECT idtipo, tipo from tipo;")
				tipos = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		tipo = request.form["tipo"]
		nombre = request.form["nombre"]
		presentacion = request.form["presentacion"]
		cantidad = request.form["cantidad"]
		try:
			conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
			try:
				with conexion.cursor() as cursor:
					consulta = "SELECT MAX(codigo) from insumos where idtipo = %s and activo = 1;"
					cursor.execute(consulta, tipo)
					maxid = cursor.fetchall()
					maxid = maxid[0][0]
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		letra = maxid[0]
		flag = 0
		straux = ""
		for i in range(len(maxid)):
			if maxid[i].isnumeric():
				straux = straux + maxid[i]
		maxid = str(int(straux) + 1)
		while len(maxid) < 3:
			maxid = '0' + maxid
		codigo = letra + str(maxid)
		try:
			conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
			try:
				with conexion.cursor() as cursor:
					consulta = "INSERT INTO insumos(idtipo, codigo, nombre, presentacion, existencia,activo) values (%s,%s,%s,%s,%s,%s);"
					cursor.execute(consulta, (tipo, codigo, nombre, presentacion, cantidad, 1))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('inicio'))
	return render_template('nuevoinsumo.html', title='Agregar insumo', tipos = tipos, logeado=logeado, idtipouser = idtipouser)

@app.route("/kardex", methods=['GET', 'POST'])
def kardex():
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
		return redirect(url_for('login'))
	data = []
	ins = ""
	existencia = 0
	idinsumo = 0
	fechaactual = datetime.now()
	actual = fechaactual.strftime("%d/%m/%Y %H:%M")
	try:
		conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
		try:
			with conexion.cursor() as cursor:
				consulta = "select codigo, nombre, presentacion from insumos where activo = 1 order by codigo asc;"
				cursor.execute(consulta)
				insumostotales = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		codigo = request.form['codigo']
		nombre = request.form['nombre']
		ins = nombre
		try:
			conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
			try:
				with conexion.cursor() as cursor:
					consulta = "select idinsumos, existencia from insumos where activo = 1 and codigo = %s;"
					cursor.execute(consulta, codigo)
					idinsumo = cursor.fetchall()
					existencia = idinsumo[0][1]
					idinsumo = idinsumo[0][0]
					consulta = 'select "Hoja de requisición", e.numhojareq, DATE_FORMAT(e.fecha,"%d/%m/%Y"), d.cantidad, u.nombre from egresosheader e inner join egresosdesc d on e.idegresosheader = d.idegresosheader inner join users u on u.idusers = d.iduser where d.idinsumo = ' + str(idinsumo) + " order by e.fecha desc;"
					cursor.execute(consulta)
					datae = cursor.fetchall()
					consulta = "select h.nombreordencompra, h.documento, DATE_FORMAT(h.fecha,'%d/%m/%Y'), d.cantidad, u.nombre from ingresosheader h inner join ingresosdesc d ON h.idingresosheader = d.idheader inner join users u ON h.user = u.idusers where d.idinsumos = " + str(idinsumo) + " order by h.fecha desc;"
					cursor.execute(consulta)
					datai = cursor.fetchall()
					for i in range(len(datae)):
						aux = datae[i]
						aux = list(aux)
						aux.insert(3, " ")
						data.append(aux)
					
					for i in range(len(datai)):
						aux = datai[i]
						aux = list(aux)
						aux.insert(4, " ")
						data.append(aux)
					
					cantdata = len(data)
					for i in range(cantdata-1):
						for j in range(cantdata-i-1):
							dia1, mes1, anio1 = [int(x) for x in data[j][2].split('/')]
							dia2, mes2, anio2 = [int(x) for x in data[j+1][2].split('/')]
							fecha1 = date(anio1, mes1, dia1)
							fecha2 = date(anio2, mes2, dia2)
							if fecha1 <  fecha2:
								data[j], data[j+1] = data[j+1], data[j]
			finally:
				conexion.close()	
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return render_template('kardex.html', title='Kardex', logeado=logeado, idtipouser = idtipouser, insumos=insumostotales, data=data, ins=ins, existencia=existencia, actual=actual, idinsumo = idinsumo)
	return render_template('kardex.html', title='Kardex', logeado=logeado, idtipouser = idtipouser, insumos=insumostotales, data=data, ins=ins, existencia=existencia, actual=actual, idinsumo = idinsumo)

@app.route("/imprimirkardex/<idinsumo>")
def imprimirkardex(idinsumo):
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
		return redirect(url_for('login'))
	fechaactual = datetime.now()
	actual = fechaactual.strftime("%d/%m/%Y %H:%M")
	try:
		conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
		try:
			with conexion.cursor() as cursor:
				consulta = "select idinsumos, existencia, codigo, nombre from insumos where activo = 1 and idinsumos = %s;"
				cursor.execute(consulta, idinsumo)
				insumo = cursor.fetchall()
				print(insumo)
				existencia = insumo[0][1]
				codigo = insumo[0][2]
				ins = insumo[0][3]
				idinsumo = insumo[0][0]
				consulta = 'select "Hoja de requisición", e.numhojareq, DATE_FORMAT(e.fecha,"%d/%m/%Y"), d.cantidad, u.nombre from egresosheader e inner join egresosdesc d on e.idegresosheader = d.idegresosheader inner join users u on u.idusers = d.iduser where d.idinsumo = ' + str(idinsumo) + " order by e.fecha desc;"
				cursor.execute(consulta)
				datae = cursor.fetchall()
				consulta = "select h.nombreordencompra, h.documento, DATE_FORMAT(h.fecha,'%d/%m/%Y'), d.cantidad, u.nombre from ingresosheader h inner join ingresosdesc d ON h.idingresosheader = d.idheader inner join users u ON h.user = u.idusers where d.idinsumos = " + str(idinsumo) + " order by h.fecha desc;"
				cursor.execute(consulta)
				datai = cursor.fetchall()
				data = []
				for i in range(len(datae)):
					aux = datae[i]
					aux = list(aux)
					aux.insert(3, " ")
					data.append(aux)
				
				for i in range(len(datai)):
					aux = datai[i]
					aux = list(aux)
					aux.insert(4, " ")
					data.append(aux)
				
				cantdata = len(data)
				for i in range(cantdata-1):
					for j in range(cantdata-i-1):
						dia1, mes1, anio1 = [int(x) for x in data[j][2].split('/')]
						dia2, mes2, anio2 = [int(x) for x in data[j+1][2].split('/')]
						fecha1 = date(anio1, mes1, dia1)
						fecha2 = date(anio2, mes2, dia2)
						if fecha1 <  fecha2:
							data[j], data[j+1] = data[j+1], data[j]
		finally:
			conexion.close()	
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	rendered = render_template('imprimirkardex.html', title='Impresión de Kardex', logeado=logeado, idtipouser = idtipouser, data=data, ins=ins, existencia=existencia, actual=actual, idinsumo = idinsumo)
	options = {'enable-local-file-access': None, 'page-size': 'Letter','margin-right': '10mm'}
	config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
	pdf = pdfkit.from_string(rendered, False, configuration=config, options=options)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = f'inline; filename=kardex{idinsumo}.pdf'
	print(response)
	return response

@app.route("/documentosingresos")
def documentosingresos():
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
		return redirect(url_for('login'))
	print(PATH_FILE)
	try:
		conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
		try:
			with conexion.cursor() as cursor:
				cursor.execute("select documento, nombreordencompra, fecha from ingresosheader group by documento order by fecha desc;")
			# Con fetchall traemos todas las filas
				facturas = cursor.fetchall()
				cantidad = len(facturas)
				existendocumentos = []
				for i in facturas:
					factura = 0
					boleta = 0
					nombrefactura = PATH_FILE + f"factura_{i[0]}.pdf"
					nombreboleta = PATH_FILE + f"boleta_{i[0]}.pdf"
					if path.exists(nombrefactura):
						factura = 1
					if path.exists(nombreboleta):
						boleta = 1
					aux = [factura, boleta]
					existendocumentos.append(aux)
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('documentosingresos.html', title='Documentos de ingresos', facturas = facturas, logeado=logeado, idtipouser = idtipouser, existendocumentos = existendocumentos, cantidad = cantidad)

@app.route("/subirdocumentos/<nomfactura>&<mensaje>", methods=['GET', 'POST'])
def subirdocumentos(nomfactura, mensaje):
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
		return redirect(url_for('login'))
	factura = 0
	boleta = 0
	nombrefactura = PATH_FILE + f"factura_{nomfactura}.pdf"
	nombreboleta = PATH_FILE + f"boleta_{nomfactura}.pdf"
	if path.exists(nombrefactura):
		factura = 1
	if path.exists(nombreboleta):
		boleta = 1
	if request.method == 'POST':
		if factura == 0:
			try:
				archivofactura = request.files['factura']
				if archivofactura.filename != '':
					if ".pdf" not in archivofactura.filename:
						if archivofactura.filename.split('.')[-1].lower() not in ['jpg', 'jpeg', 'png', 'gif']:
							mensaje = 1
							return redirect(url_for('subirdocumentos', nomfactura = nomfactura, mensaje = mensaje))
						else:
							archivofactura.save('temp.png')
							if archivofactura.filename.split('.')[-1].lower() == 'png':
								img = Image.open('temp.png')
								rgb_img = img.convert('RGB')
								rgb_img.save('temp.jpg')
								imagen_path = 'temp.jpg'
							else:
								imagen_path = 'temp.png'
							pdf = FPDF('P', 'mm', 'Letter')  # Ajustar a tamaño Carta
							pdf.add_page()
							pdf.image(imagen_path, 0, 0, 215.9, 279.4)
							pdf.output(path.join(PATH_FILE, f"factura_{nomfactura}.pdf"), 'F')
							os.remove(imagen_path)
					else:
						archivofactura.save(path.join(PATH_FILE, f"factura_{nomfactura}.pdf"))
			except:
				print("No subió documento factura")
		if boleta == 0:
			try:
				archivoboleta = request.files['boleta']
				if archivoboleta.filename != '':
					if ".pdf" not in archivoboleta.filename:
						if archivoboleta.filename.split('.')[-1].lower() not in ['jpg', 'jpeg', 'png', 'gif']:
							mensaje = 1
							return redirect(url_for('subirdocumentos', nomfactura = nomfactura, mensaje = mensaje))
						else:
							archivoboleta.save('temp.png')
							if archivoboleta.filename.split('.')[-1].lower() == 'png':
								img = Image.open('temp.png')
								rgb_img = img.convert('RGB')
								rgb_img.save('temp.jpg')
								imagen_path = 'temp.jpg'
							else:
								imagen_path = 'temp.png'
							pdf = FPDF('P', 'mm', 'Letter')  # Ajustar a tamaño Carta
							pdf.add_page()
							print("Llego")
							pdf.image(imagen_path, 0, 0, 215.9, 279.4)
							pdf.output(path.join(PATH_FILE, f"boleta_{nomfactura}.pdf"), 'F')
							os.remove(imagen_path)
					else:
						archivoboleta.save(path.join(PATH_FILE, f"boleta_{nomfactura}.pdf"))
			except:
				print("No subió documento orden")
		return redirect(url_for('documentosingresos'))
	return render_template('subirdocumentos.html', title='Adjuntar documentos', logeado=logeado, factura=factura, boleta = boleta, mensaje = mensaje)

@app.route("/verdocumento/<nombredocumento>", methods=['GET', 'POST'])
def verdocumento(nombredocumento):
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
		return redirect(url_for('login'))
	return render_template('verdocumento.html', title='Visualización de Documento', logeado=logeado, nombredocumento = nombredocumento)

@app.route("/egresoinsumos", methods=['GET', 'POST'])
def egresoinsumos():
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
		return redirect(url_for('login'))
	try:
		conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
		try:
			with conexion.cursor() as cursor:
				consulta = "select codigo, nombre, presentacion from insumos where activo = 1 order by codigo asc;"
				cursor.execute(consulta)
				insumostotales = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		fecha = request.form['fecha']
		cantidad = request.form['cantidad']
		pacientes = request.form['pacientes']
		numhojareq = request.form['numhojareq']
		numhojareq = "Hoja de requisición " + str(numhojareq)
		try:
			conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
			try:
				with conexion.cursor() as cursor:
					consulta = "INSERT INTO egresosheader(fecha, numpacientes, numhojareq) VALUES (%s, %s, %s);"
					cursor.execute(consulta, (fecha, pacientes, numhojareq))
					conexion.commit()
					consulta = "select MAX(idegresosheader) from egresosheader;"
					cursor.execute(consulta)
					idheader = cursor.fetchall()
					idheader = idheader[0][0]
					for i in range(int(cantidad)):
						aux = 'codigo' + str(i)
						codigo = request.form[aux]
						aux = 'cantidad' + str(i)
						cant = request.form[aux]
						consulta = "select idinsumos, existencia from insumos where codigo = %s and activo = 1;"
						cursor.execute(consulta, codigo)
						idinsumo = cursor.fetchall()
						existencia = idinsumo[0][1]
						idinsumo = idinsumo[0][0]
						consulta = "INSERT INTO egresosdesc(idegresosheader, idinsumo, cantidad, iduser) VALUES(%s, %s, %s, %s);"
						cursor.execute(consulta, (idheader, idinsumo, cant, session['iduserldd']))
						existencia = existencia - float(cant)
						consulta = "update insumos set existencia = %s where idinsumos = %s;"
						cursor.execute(consulta, (existencia, idinsumo))
						conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('kardex'))
	return render_template('egresoinsumos.html', title='Egreso de Insumos', logeado=logeado, idtipouser = idtipouser, insumos = insumostotales)

@app.route("/inextra", methods=['GET', 'POST'])
def inextra():
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
		return redirect(url_for('login'))
	try:
		conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
		try:
			with conexion.cursor() as cursor:
				consulta = "select codigo, nombre, presentacion from insumos where activo = 1 order by codigo asc;"
				cursor.execute(consulta)
				insumostotales = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		razon = request.form['razon']
		fecha = request.form['fecha']
		cantidad = request.form['cantidad']
		numhojareq = request.form['numhojareq']
		numhojareq = "Formulario de Ingreso " + str(numhojareq)
		try:
			conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
			try:
				with conexion.cursor() as cursor:
					consulta = "INSERT INTO ingresosheader(nombreordencompra, documento, fecha, user) VALUES (%s, %s, %s, %s);"
					cursor.execute(consulta, (razon, numhojareq, fecha, session['iduserldd']))
					conexion.commit()
					consulta = "select MAX(idingresosheader) from ingresosheader;"
					cursor.execute(consulta)
					idheader = cursor.fetchall()
					idheader = idheader[0][0]
					for i in range(int(cantidad)):
						aux = 'codigo' + str(i)
						codigo = request.form[aux]
						aux = 'cantidad' + str(i)
						cant = request.form[aux]
						consulta = "select idinsumos, existencia from insumos where codigo = %s and activo=1;"
						cursor.execute(consulta, codigo)
						idinsumo = cursor.fetchall()
						existencia = idinsumo[0][1]
						existencia = existencia + float(cant)
						idinsumo = idinsumo[0][0]
						consulta = "INSERT INTO ingresosdesc(idheader, idinsumos, cantidad) VALUES(%s, %s, %s);"
						cursor.execute(consulta, (idheader, idinsumo, cant))
						consulta = "update insumos set existencia=%s where idinsumos = %s;"
						cursor.execute(consulta, (existencia, idinsumo))
						conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('kardex'))
	return render_template('inextra.html', title='Ingreso extraordinario', logeado=logeado, idtipouser = idtipouser, insumos = insumostotales)

@app.route("/ingresoinsumos", methods=['GET', 'POST'])
def ingresoinsumos():
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
		return redirect(url_for('login'))
	try:
		conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
		try:
			with conexion.cursor() as cursor:
				consulta = "select codigo, nombre, presentacion from insumos where activo = 1 order by codigo asc;"
				cursor.execute(consulta)
				insumostotales = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		razon = request.form['razon']
		fecha = request.form['fecha']
		cantidad = request.form['cantidad']
		numhojareq = request.form['numhojareq']
		numhojareq = "Documento " + str(numhojareq)
		try:
			conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
			try:
				with conexion.cursor() as cursor:
					consulta = "INSERT INTO ingresosheader(nombreordencompra, documento, fecha, user) VALUES (%s, %s, %s, %s);"
					cursor.execute(consulta, (razon, numhojareq, fecha, session['iduserldd']))
					conexion.commit()
					consulta = "select MAX(idingresosheader) from ingresosheader;"
					cursor.execute(consulta)
					idheader = cursor.fetchall()
					idheader = idheader[0][0]
					for i in range(int(cantidad)):
						aux = 'codigo' + str(i)
						codigo = request.form[aux]
						aux = 'cantidad' + str(i)
						cant = request.form[aux]
						consulta = "select idinsumos, existencia from insumos where codigo = %s and activo=1;"
						cursor.execute(consulta, codigo)
						idinsumo = cursor.fetchall()
						existencia = idinsumo[0][1]
						existencia = existencia + float(cant)
						idinsumo = idinsumo[0][0]
						consulta = "INSERT INTO ingresosdesc(idheader, idinsumos, cantidad) VALUES(%s, %s, %s);"
						cursor.execute(consulta, (idheader, idinsumo, cant))
						consulta = "update insumos set existencia=%s where idinsumos = %s;"
						cursor.execute(consulta, (existencia, idinsumo))
						conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('kardex'))
	return render_template('ingresoinsumos.html', title='Ingreso Insumos', logeado=logeado, idtipouser = idtipouser, insumos = insumostotales)

@app.route('/hojareq', methods=['GET', 'POST'])
def hojareq():
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
		return redirect(url_for('login'))
	#Se genera el PDF
	rendered = render_template('hojareq.html', title="Hoja de Requisición")
	options = {'enable-local-file-access': None, 'page-size': 'Letter','margin-right': '10mm'}
	config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
	pdf = pdfkit.from_string(rendered, False, configuration=config, options=options)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'inline; filename=hojarequisicion.pdf'
	print(response)
	return response

@app.route('/hojaingresoextra', methods=['GET', 'POST'])
def hojaingresoextra():
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
		return redirect(url_for('login'))
	#Se genera el PDF
	rendered = render_template('hojaingresoextra.html', title="Hoja de Ingreso Extraordinario")
	options = {'enable-local-file-access': None, 'page-size': 'Letter','margin-right': '10mm'}
	config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
	pdf = pdfkit.from_string(rendered, False, configuration=config, options=options)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'inline; filename=hojaringresoextraordinario.pdf'
	print(response)
	return response

@app.route("/equipo")
def equipo():
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
		try:
			with conexion.cursor() as cursor:
				cursor.execute("SELECT idequipo, nombre, codigo, marca, activo, razonbaja, DATE_FORMAT(fechabaja,'%d/%m/%Y') from equipo order by codigo asc;")
			# Con fetchall traemos todas las filas
				equipos = cursor.fetchall()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('equipo.html', title='Equipos',equipos = equipos, logeado=logeado, idtipouser = idtipouser)

@app.route("/nuevoequipo", methods=['GET', 'POST'])
def nuevoequipo():
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
		return redirect(url_for('login'))
	if request.method == 'POST':
		nombre = request.form["nombre"]
		marca = request.form["marca"]
		try:
			conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
			try:
				with conexion.cursor() as cursor:
					consulta = "SELECT MAX(codigo) from equipo;"
					cursor.execute(consulta)
					maxid = cursor.fetchall()
					maxid = maxid[0][0]
					if maxid != None:
						straux = ""
						for i in range(len(maxid)):
							if maxid[i].isnumeric():
								straux = straux + maxid[i]
						maxid = str(int(straux) + 1)
						while len(maxid) < 3:
							maxid = '0' + maxid
						codigo = "E" + str(maxid)
					else:
						codigo = "E001"
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		

		try:
			conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
			try:
				with conexion.cursor() as cursor:
					consulta = "INSERT INTO equipo(nombre, codigo, marca, activo) values (%s,%s,%s,1);"
					cursor.execute(consulta, (nombre, codigo, marca))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('equipo'))
	return render_template('nuevoequipo.html', title='Agregar Equipo', logeado=logeado, idtipouser = idtipouser)

@app.route("/editarequipo/<id>", methods=['GET', 'POST'])
def editarequipo(id):
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
		return redirect(url_for('login'))
	try:
		conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
		try:
			with conexion.cursor() as cursor:
				consulta = "select nombre, marca from equipo where idequipo = %s;"
				cursor.execute(consulta, (id))
				equipo = cursor.fetchone()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	if request.method == 'POST':
		nombre = request.form["nombre"]
		marca = request.form["marca"]
		try:
			conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
			try:
				with conexion.cursor() as cursor:
					consulta = "update equipo set nombre = %s, marca = %s where idequipo = %s;"
					cursor.execute(consulta, (nombre, marca, id))
				conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('equipo'))
	return render_template('editarequipo.html', title='Editar Equipo', logeado=logeado, idtipouser = idtipouser, equipo = equipo)

@app.route("/mantenimientos/<id>")
def mantenimientos(id):
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
	try:
		conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
		try:
			with conexion.cursor() as cursor:
				consulta = f"SELECT idmantenimiento, proveedor, DATE_FORMAT(fecha,'%d/%m/%Y'), documento from mantenimiento where idequipo = {id} order by fecha desc;"
				cursor.execute(consulta)
			# Con fetchall traemos todas las filas
				mantenimientos = cursor.fetchall()
				consulta = "SELECT nombre, codigo, marca from equipo where idequipo = %s;"
				cursor.execute(consulta, id)
			# Con fetchall traemos todas las filas
				equipo = cursor.fetchone()
		finally:
			conexion.close()
	except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
		print("Ocurrió un error al conectar: ", e)
	return render_template('mantenimientos.html', title='Mantenimientos', mantenimientos = mantenimientos, logeado=logeado, idtipouser = idtipouser, equipo=equipo, id=id)

@app.route("/nuevomantenimiento/<id>", methods=['GET', 'POST'])
def nuevomantenimiento(id):
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
	if request.method == 'POST':
		proveedor = request.form["proveedor"]
		fecha = request.form["fecha"]
		try:
			conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
			try:
				with conexion.cursor() as cursor:
					consulta = "insert into mantenimiento(idequipo, fecha, documento, proveedor) values (%s, %s, 0, %s);"
					cursor.execute(consulta, (id,fecha,proveedor))
				# Con fetchall traemos todas las filas
					conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('mantenimientos', id = id))
	return render_template('nuevomantenimiento.html', title='Nuevo Mantenimiento', logeado=logeado, idtipouser = idtipouser)

@app.route("/subirdocumentomantenimiento/<idmantenimiento>&<mensaje>", methods=['GET', 'POST'])
def subirdocumentomantenimiento(idmantenimiento, mensaje):
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
		return redirect(url_for('login'))
	existe = 0
	nombrearchivo = PATH_FILE + f"mantenimiento_{idmantenimiento}.pdf"
	if path.exists(nombrearchivo):
		existe = 1
	if request.method == 'POST':
		if existe == 0:
			try:
				archivomantenimiento = request.files['documento']
				if archivomantenimiento.filename != '':
					if ".pdf" not in archivomantenimiento.filename:
						if archivomantenimiento.filename.split('.')[-1].lower() not in ['jpg', 'jpeg', 'png', 'gif']:
							mensaje = 1
							return redirect(url_for('subirdocumentomantenimiento', idmantenimiento = idmantenimiento, mensaje = mensaje))
						else:
							archivomantenimiento.save('temp.png')
							if archivomantenimiento.filename.split('.')[-1].lower() == 'png':
								img = Image.open('temp.png')
								rgb_img = img.convert('RGB')
								rgb_img.save('temp.jpg')
								imagen_path = 'temp.jpg'
							else:
								imagen_path = 'temp.png'
							pdf = FPDF('P', 'mm', 'Letter')  # Ajustar a tamaño Carta
							pdf.add_page()
							pdf.image(imagen_path, 0, 0, 215.9, 279.4)
							pdf.output(path.join(PATH_FILE, f"mantenimiento_{idmantenimiento}.pdf"), 'F')
							os.remove(imagen_path)
					else:
						archivomantenimiento.save(path.join(PATH_FILE, f"mantenimiento_{idmantenimiento}.pdf"))
					try:
						conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
						try:
							with conexion.cursor() as cursor:
								consulta = "update mantenimiento set documento = 1 where idmantenimiento = %s;"
								cursor.execute(consulta, (idmantenimiento))
							# Con fetchall traemos todas las filas
								conexion.commit()
						finally:
							conexion.close()
					except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
						print("Ocurrió un error al conectar: ", e)
			except:
				print("No subió documento del mantenimiento")
		return redirect(url_for('equipo'))
	return render_template('subirdocumentomantenimiento.html', title='Adjuntar documentos', logeado=logeado, mensaje = mensaje, idtipouser = idtipouser)

@app.route("/darbajaequipo/<id>", methods=['GET', 'POST'])
def darbajaequipo(id):
	try:
		logeado = session['logeadoldd']
		idtipouser = session['idtipouserldd']
	except:
		logeado = 0
		idtipouser = 0
	if request.method == 'POST':
		razon = request.form["razon"]
		fecha = request.form["fecha"]
		try:
			conexion = pymysql.connect(host=Conhost, user=Conuser, password=Conpassword, db=Condb)
			try:
				with conexion.cursor() as cursor:
					consulta = "update equipo set activo = 0, razonbaja = %s, fechabaja = %s where idequipo = %s;"
					cursor.execute(consulta, (razon, fecha, id))
				# Con fetchall traemos todas las filas
					conexion.commit()
			finally:
				conexion.close()
		except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
			print("Ocurrió un error al conectar: ", e)
		return redirect(url_for('equipo'))
	return render_template('darbajaequipo.html', title='Dar Baja a Equipo', logeado=logeado, idtipouser = idtipouser)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5006)