import requests
import networkx as nx
import openpyxl
from difflib import SequenceMatcher
from datetime import datetime

from bs4 import BeautifulSoup

from app.example.models.producto import Articulo
from app.example.models.error_dato import ErrorDato
from app.example.models.investigador import Investigador
from app.example.models.investigador_grupo import InvestigadorGrupo


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def extraction(cadena, str_ini=None, str_fin=None):
    if str_fin is not None:
        if str_ini is not None:
            indice_c = cadena.index(str_ini)  # obtenemos la posición del carácter c
            indice_h = cadena.index(str_fin)  # obtenemos la posición del carácter h
            found_text = cadena[indice_c:indice_h]
        else:
            indice_h = cadena.index(str_fin)  # obtenemos la posición del carácter h
            found_text = cadena[:indice_h]
    else:
        indice_c = cadena.index(str_ini)  # obtenemos la posición del carácter c
        found_text = cadena[indice_c:]
    return found_text


def extraction_position(cadena, indice_c=0, indice_h=0):
    found_text = cadena[indice_c:len(cadena) - indice_h]
    return found_text


def normalize(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("È", "E"),
        ("Ñ", "N"),
        ("Ò", "O"),
        ("?", ""),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s


def validar(cadena):
    search = (
        "INDUSTRI",
        "MINISTR",
        "PRESIDEN",
        "VICEM",
        "ACOMPA",

    )
    for x in search:
        if cadena.find('la'):
            return True

    return False


def normalize_frases(cadena):
    replacements = (
        "H.R:",
        "H.R.",
        "H.S:",
        "H.S.",
        "H.S",
        "HS:",
        "DOCTOR",
        "DR.",
        "DRA."
        "HR.",
        "HR",

    )
    cadena = cadena.rstrip(".")
    for x in replacements:
        cadena = cadena.replace(x, "", 1)

    cadena = cadena.rstrip()
    cadena = cadena.lstrip()
    cadena = cadena.rstrip(".")
    return cadena


def normalize_spaces(cadena):
    cadena = cadena.rstrip()
    cadena = cadena.lstrip()
    return cadena


autores_procesados = list()


def articulos_grupo(grupos, estado=None, year=None, type="Group"):
    lista_group = list()
    if len(autores_procesados) <= 0:
        investigadores = Investigador.get_all()
        for inv in investigadores:
            autores_procesados.append(inv.nombre)

    if type == "Group":
        lista_group = autoresgrupo(grupos, estado)
    else:
        lista_group = grupos.split(",")

    articulosvsautores(lista_group, year, grupos)


def articulosvsautores(mi_lista=None, year=None, grupos=None):
    if not mi_lista:
        return

    # M = nx.Graph()

    # documents_management = list()
    # documents_management.append(('author', 'title', 'year', 'review'))

    for cvlac_enlace in mi_lista:
        cvlac_datas = cvlac_enlace.split("-")
        cvlac_id = cvlac_datas[0]
        cvlac_name = ""
        cvlac_ini = None
        cvlac_ini_mes = None
        cvlac_fin = None
        cvlac_fin_mes = None
        cvlac_actual = 0
        if len(cvlac_datas) > 1:
            cvlac_name = cvlac_datas[1]
            cvlac_ini = normalize_spaces(cvlac_datas[2])
            if cvlac_ini:
                cvlac_ini = cvlac_ini.split("/")
                cvlac_ini_mes = cvlac_ini[1]
                cvlac_ini = cvlac_ini[0]

            cvlac_fin = normalize_spaces(cvlac_datas[3])
            if cvlac_fin == "Actual":
                cvlac_actual = 1
                cvlac_fin = None
            else:
                cvlac_fin = cvlac_fin.split("/")
                cvlac_fin_mes = cvlac_fin[1]
                if cvlac_fin_mes == "null":
                    cvlac_fin_mes = 12
                cvlac_fin = cvlac_fin[0]

        r = requests.get(
            'https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh=' + cvlac_id,
            verify=False)
        soup = BeautifulSoup(r.text, 'lxml')
        print(cvlac_id)
        bloqueada = soup.find("blockquote",
                              text="La información de este currículo no está disponible por solicitud del investigador")
        if bloqueada:
            continue

        formacion = soup.find("h3",
                              text="Formación Académica")

        if not formacion:
            continue

        tables = soup.find_all('table')

        datos_basicos = tables[1]

        categoria = datos_basicos.find("td", text="Categoría")
        if categoria:
            categoria = categoria.find_next_sibling("td").text
            categoria = normalize_spaces(categoria.split(")")[0] + ")")
        else:
            categoria = ''
        nombre = datos_basicos.find("td", text="Nombre").find_next_sibling("td").text
        nombre = normalize(nombre)
        nombre = normalize_spaces(nombre)
        nombre = nombre.upper()
        nacionalidad = datos_basicos.find("td", text="Nacionalidad").find_next_sibling("td").text
        sexo = datos_basicos.find("td", text="Sexo").find_next_sibling("td").text

        investigador_actual = Investigador.get_by_id(cvlac_id)
        if not investigador_actual:
            investigador = Investigador(codigo=cvlac_id, nombre=nombre, genero=sexo, nacionalidad=nacionalidad,
                                        categoria=categoria, fecha=datetime.today())
            investigador.save()

        investigador_grupo_actual = InvestigadorGrupo.simple_filter(grupo_id=grupos, investigador_id=cvlac_id)
        if not investigador_grupo_actual:
            investigador_grupo = InvestigadorGrupo(grupo_id=grupos, investigador_id=cvlac_id, anoini=cvlac_ini,
                                                   mesini=cvlac_ini_mes, anofin=cvlac_fin, mesfin=cvlac_fin_mes,
                                                   actual=cvlac_actual)
            investigador_grupo.save()

        if investigador_actual:
            continue

        articles = soup.find("h3",
                             text="Artículos")

        if not articles:
            continue

        posicion = 0
        for table in tables:

            titulo_h3 = table.find('h3')

            if titulo_h3:
                titulo = titulo_h3.getText()

                if titulo == "Artículos":
                    blockquotes = table.find_all('blockquote')

                    for blockquote in blockquotes:
                        #try:
                        articulo_data = blockquote.getText()
                        error_dato = ErrorDato(texto=articulo_data, investigador=cvlac_id, grupo=grupos,
                                               estado="ok")
                        error_dato.save()
                        '''
                        cadena_autor = extraction(articulo_data, str_fin='"')
                        autores_list = cadena_autor.split(",")
                        for i, autor in enumerate(autores_list):
                            autores_list[i] = normalize_spaces(autores_list[i])

                        if set(autores_list) & set(autores_procesados):
                            continue

                        cadena_titulo = extraction(articulo_data, str_ini='"', str_fin='En:')
                        cadena_titulo = extraction_position(cadena_titulo, 1, 2).rstrip()
                        cadena_titulo = extraction_position(cadena_titulo, 0, 1)
                        if cadena_titulo == "" or cadena_titulo == " ":
                            continue
                        cadena_journal = extraction(articulo_data, str_ini='En:', str_fin='ISSN:')
                        cadena_journals = cadena_journal.split("\n")
                        cadena_country = cadena_journals[0]
                        cadena_review = cadena_journals[1].lstrip()
                        cadena_country = extraction_position(cadena_country, 4, 2)
                        cadena_year = extraction(articulo_data, str_fin='DOI')
                        cadena_year = cadena_year.rstrip()
                        cadena_year = cadena_year[-5:-1]
                        if not year or int(cadena_year) >= year:

                            for autor in autores_list:
                                # autor = normalize_frases(autor)

                                # ratio = SequenceMatcher(None, y, x).ratio()
                                if autor == "":
                                    continue

                                # documents_management.append((autor, cadena_titulo, cadena_year, cadena_review))
                                #                            M.add_node(autor, type="autor", label_autor=autor)
                                #                            M.add_node(cadena_titulo, type="articulo", year=cadena_year, review=cadena_review,
                                #                                       country=cadena_country)
                                #                            M.add_edge(autor, cadena_titulo)
                                articulo = Articulo(investigador=autor, articulo=cadena_titulo, year=cadena_year,
                                                    review=cadena_review, pais=cadena_country, doi='')
                                articulo.save()

                        #except:
                        #    error_dato = ErrorDato(texto=blockquote.getText(), investigador=cvlac_id, grupo=grupos, estado="error")
                        #    error_dato.save()
                        '''
                    break
            # else:
            posicion = posicion + 1
        print(cvlac_name)
        autores_procesados.append(cvlac_name)
        print("end")
    # nx.write_gexf(M, "articulosvsautores_upb.gexf")
    # export_excel(documents_management)


def autoresgrupo(grupos, estado=None):
    mi_lista = []

    grupos_ids = grupos.split(",")

    for grupo_id in grupos_ids:

        r = requests.get('https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro=' + grupo_id,
                         verify=False)
        soup = BeautifulSoup(r.text, 'lxml')

        tables = soup.find_all('table')

        for table in tables:
            titulo_td = table.find('td', {'class': 'celdaEncabezado'})

            if titulo_td:
                titulo = titulo_td.getText()

                if titulo == "Integrantes del grupo":
                    trs = table.find_all('tr')
                    for tr in trs:
                        tds = tr.find_all('td')
                        enlace = tds[0].find_all('a')
                        if not enlace:
                            continue

                        actual = tds[3].getText()

                        enlace_data = enlace[0]['href'].split("=")[1]

                        enlace_name = enlace[0].getText()
                        enlace_name = normalize(enlace_name)
                        enlace_name = enlace_name.replace("-", " ")
                        enlace_name = enlace_name.replace("*", " ")
                        enlace_name = enlace_name.lstrip()
                        enlace_name = enlace_name.rstrip()
                        enlace_name = enlace_name.upper()

                        enlace_data = enlace_data + "-" + enlace_name + "-" + actual

                        mi_lista.append(enlace_data)
                    continue
    return mi_lista


def export_excel(lista, name='data_export_upb.xlsx'):
    wb = openpyxl.Workbook()
    hoja = wb.active
    # Crea la fila del encabezado con los títulos

    for objeto in lista:
        hoja.append(objeto)

    wb.save(name)


'''
def totalgrupos(id_inicial=1, id_final=50):
    mi_lista = []

    grupos_ids = grupos.split(",")

    estado = 0
    mi_lista.append(('codigo', 'nombre', 'institucion', 'ubicacion', 'clasificacion', 'year', 'area'))
    for x in range(id_inicial, id_final):
        print (str(x).rjust(14, '0'))
        codigo = (str(x).rjust(14, '0'))
        r = requests.get('https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro='+codigo, verify=False)
        soup = BeautifulSoup(r.text, 'lxml')

        datos_basicos = soup.find("td", text="Datos básicos")
        if not datos_basicos:
            continue

        tables = soup.find_all('table')

        ubicacion = ""
        institucion = ""
        nombre = soup.find("span")
        nombre = nombre.text
        #print(nombre)
        for table in tables:
            titulo_td = table.find('td', {'class': 'celdaEncabezado'})

            if titulo_td:
                titulo = titulo_td.getText()

                if titulo == "Datos básicos":
                    #trs = table.find_all('tr')
                    ubicacion = table.find("td", text="Departamento - Ciudad").find_next_sibling("td").text
                    clasificacion = table.find("td", text="Clasificación").find_next_sibling("td").text
                    area = table.find("td", text="Área de conocimiento").find_next_sibling("td").text
                    area = normalize_spaces(area)
                    year = table.find("td", text="Año y mes de formación").find_next_sibling("td").text
                    #print(ubicacion)
                    continue


                if titulo == "Instituciones":

                    institucion = table.find('td', {'class': 'celdas1'})
                    if institucion:
                        institucion = normalize_spaces(institucion.text)

                    mi_lista.append((codigo, nombre, ubicacion, institucion, clasificacion, year, area))
                    break

    export_excel(mi_lista, name="grupos" + str(id_final) + ".xlsx")
    return mi_lista
'''
