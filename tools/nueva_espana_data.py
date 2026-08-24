"""Datos de la página de la Nueva España, 1519 a 1853.

Todo lo que va aquí lleva año y fuente. Donde las fuentes no coinciden se
guarda la discrepancia en el campo de nota y la página la enseña, en lugar de
escoger una fecha y callar la otra.

Las coordenadas de los lugares que todavía existen vienen del buscador de
Open-Meteo, que corre sobre GeoNames. Las de los sitios arqueológicos o los
parajes sin pueblo encima van marcadas como aproximadas y se dan a mano; para
esas la página dice que lo son.
"""

# ---------------------------------------------------------------- lugares
# nombre: (lat, lon, exacto)   exacto=False significa posición aproximada
LUGARES = {
    # la costa y el camino a Tenochtitlan
    "San Juan de Ulúa": (19.2080, -96.1300, True),
    "Cempoala": (19.4453, -96.4017, False),
    "Quiahuiztlán": (19.6667, -96.3833, False),
    "La Antigua": (19.3222, -96.3210, True),
    "Xalapa": (19.5312, -96.9159, True),
    "Tlaxcala": (19.3178, -98.2385, True),
    "Cholula": (19.0641, -98.3035, True),
    "Paso de Cortés": (19.0833, -98.6500, False),
    "Amecameca": (19.1238, -98.7665, True),
    "Iztapalapa": (19.3550, -99.0600, False),
    "México-Tenochtitlan": (19.4326, -99.1332, True),
    # el occidente y el camino de la plata
    "Tepic": (21.5073, -104.8933, True),
    "Compostela": (21.2373, -104.9006, True),
    "Culiacán": (24.8021, -107.3942, True),
    "Nochistlán": (21.3636, -102.8475, True),
    "Guadalajara": (20.6774, -103.3475, True),
    "Zacatecas": (22.7684, -102.5814, True),
    "Durango": (24.0203, -104.6576, True),
    "Santa Bárbara": (26.8026, -105.8196, True),
    "Saltillo": (25.4260, -100.9796, True),
    "Monterrey": (25.6843, -100.3172, True),
    "Monclova": (26.9069, -101.4206, True),
    "Chihuahua": (28.6353, -106.0889, True),
    "Puebla": (19.0478, -98.2072, True),
    "Veracruz": (19.1809, -96.1429, True),
    "Laredo": (27.5064, -99.5075, True),
    "Ojinaga": (29.5669, -104.5449, True),
    "Ures": (29.4271, -110.3876, True),
    # el norte
    "El Paso del Norte": (31.7587, -106.4869, True),
    "San Juan de los Caballeros": (36.0500, -106.0700, False),
    "Santa Fe": (35.6870, -105.9378, True),
    "Acoma": (34.8967, -107.5817, False),
    "Tiguex": (35.3000, -106.5511, False),
    "Hawikuh": (35.0725, -108.8506, False),
    "Chichilticalli": (32.7000, -110.2000, False),
    "Gran Cañón": (36.0600, -112.1400, False),
    "Quivira": (38.3450, -98.2017, False),
    "Palo Duro": (34.9400, -101.6600, False),
    "Albuquerque": (35.0845, -106.6511, True),
    "San Antonio": (29.4241, -98.4936, True),
    "Galveston": (29.3013, -94.7977, True),
    "Apalachicola": (29.7300, -84.9900, False),
    "Boca del Misisipi": (29.1500, -89.2500, False),
    "Tampa": (27.9475, -82.4584, True),
    # la Pimería y las Californias
    "Dolores": (30.7500, -110.8500, False),
    "Magdalena de Kino": (30.6268, -110.9615, True),
    "Caborca": (30.7183, -112.1584, True),
    "Guevavi": (31.4700, -110.9300, False),
    "San Xavier del Bac": (32.1070, -111.0080, False),
    "Tucson": (32.2217, -110.9265, True),
    "Tubac": (31.6126, -111.0459, True),
    "Yuma": (32.7253, -114.6244, True),
    "Boca del Colorado": (31.8000, -114.8000, False),
    "Loreto": (26.0122, -111.3489, True),
    "Velicatá": (29.9700, -114.7000, False),
    "San Diego": (32.7157, -117.1647, True),
    "San Gabriel": (34.0961, -118.1058, False),
    "Los Ángeles": (34.0522, -118.2437, True),
    "Santa Bárbara de la Alta California": (34.4208, -119.6982, True),
    "Monterey": (36.6002, -121.8947, True),
    "San Francisco": (37.7749, -122.4194, True),
    "Sierra de Sweeney": (37.6100, -122.4500, False),
    # el altiplano y la mar del norte
    "Lago de Utah": (40.2200, -111.8000, False),
    "Vado de los Padres": (37.0000, -111.2500, False),
    "Durango de Colorado": (37.2753, -107.8801, True),
    "Barra de Navidad": (19.2000, -104.6800, False),
    "Acapulco": (16.8494, -99.9089, True),
    "San Blas": (21.5408, -105.2880, True),
    "Cabo Mendocino": (40.4400, -124.4000, False),
    "Boca del Columbia": (46.2500, -124.0000, False),
    "Cabo Blanco": (42.8400, -124.5600, False),
    "Punta de los Mártires": (47.3000, -124.2700, False),
    "Nutka": (49.6000, -126.6000, False),
    "Bahía de Sitka": (56.1300, -135.4000, False),
}

# ------------------------------------------------------- las primeras horas
# La llegada, tramo por tramo. Cada tramo lleva el año en que se anduvo.
LLEGADA = [
    ("San Juan de Ulúa", 1519), ("Cempoala", 1519), ("Quiahuiztlán", 1519),
    ("Xalapa", 1519), ("Tlaxcala", 1519), ("Cholula", 1519),
    ("Paso de Cortés", 1519), ("Iztapalapa", 1519), ("México-Tenochtitlan", 1519),
]

# ------------------------------------------------------------- las entradas
# nombre, quién, año de salida, año de regreso, camino, nota
ENTRADAS = [
    ("Nueva Galicia", "Nuño de Guzmán", 1530, 1536,
     ["México-Tenochtitlan", "Nochistlán", "Tepic", "Compostela", "Culiacán"],
     "El reino de Nueva Galicia se creó por real cédula del 25 de enero de 1531"),
    ("La caminata", "Álvar Núñez Cabeza de Vaca", 1528, 1536,
     ["Tampa", "Apalachicola", "Boca del Misisipi", "Galveston", "Ojinaga",
      "Ures", "Culiacán", "México-Tenochtitlan"],
     "El camino de tierra adentro se discute hasta hoy: esta línea es el "
     "corredor que más se repite, no una ruta levantada"),
    ("Cíbola y Quivira", "Francisco Vázquez de Coronado", 1540, 1542,
     ["Compostela", "Culiacán", "Chichilticalli", "Hawikuh", "Tiguex",
      "Palo Duro", "Quivira"],
     "De esta entrada salieron las primeras noticias del Gran Cañón, adonde "
     "llegó García López de Cárdenas"),
    ("Nueva Vizcaya", "Francisco de Ibarra", 1562, 1567,
     ["Zacatecas", "Durango", "Santa Bárbara"],
     "Ibarra fundó Durango en 1563 y Santa Bárbara en 1567; otras jornadas "
     "que se le atribuyen no se pudieron confirmar"),
    ("Nuevo México", "Juan de Oñate", 1598, 1605,
     ["Santa Bárbara", "El Paso del Norte", "San Juan de los Caballeros",
      "Acoma", "Quivira"],
     "En 1604 bajó al Colorado y volvió en enero de 1605; en Acoma, en 1599, "
     "su gente mató a unos ochocientos y mutiló a los presos"),
    ("La Pimería Alta", "Eusebio Francisco Kino", 1687, 1711,
     ["Dolores", "Magdalena de Kino", "Caborca", "Guevavi", "San Xavier del Bac",
      "Boca del Colorado"],
     "Kino probó que la California era península y no isla"),
    ("La Alta California", "Gaspar de Portolá y Junípero Serra", 1769, 1770,
     ["Loreto", "Velicatá", "San Diego", "Monterey", "Sierra de Sweeney"],
     "El 1 de noviembre de 1769 los exploradores de José Francisco Ortega "
     "vieron por primera vez la bahía de San Francisco"),
    ("El camino de Sonora", "Juan Bautista de Anza", 1774, 1776,
     ["Tubac", "Yuma", "San Gabriel", "Monterey", "San Francisco"],
     "La primera jornada fue en 1774; la segunda llevó pobladores y en marzo "
     "de 1776 escogió el sitio del presidio de San Francisco"),
    ("Hacia Monterey por tierra", "Domínguez y Vélez de Escalante", 1776, 1777,
     ["Santa Fe", "Durango de Colorado", "Lago de Utah", "Vado de los Padres",
      "Santa Fe"],
     "No llegaron a California: dieron la vuelta y su camino quedó como el "
     "primer tramo de la Vieja Vereda Española"),
    ("La mar del norte", "Juan Pérez, Heceta y Bodega y Quadra", 1774, 1775,
     ["San Blas", "Monterey", "Cabo Mendocino", "Boca del Columbia",
      "Punta de los Mártires", "Nutka"],
     "Pérez llegó a los 54 grados y 40 minutos en 1774 y la Sonora a los 56 "
     "grados y 8 minutos el 15 de agosto de 1775, arriba del cuadro"),
]

# --------------------------------------------------------------- las villas
# nombre, año, nota
VILLAS = [
    ("Veracruz", 1519, "La villa se asentó tres veces: el sitio de 1519, La "
     "Antigua desde 1525 y el sitio de hoy por cédula de 1599"),
    ("Puebla", 1531, "Trazada el 16 de abril de 1531"),
    ("Guadalajara", 1542, "Cuarto asiento, en el valle de Atemajac, el 14 de "
     "febrero de 1542; los tres anteriores fueron 1532, 1533 y 1541"),
    ("Zacatecas", 1546, "Hallado el 8 de septiembre de 1546; la fundación "
     "formal se fecha en 1548"),
    ("Durango", 1563, "8 de julio de 1563"),
    ("Saltillo", 1577, "La fecha exacta no consta: Alberto del Canto la asentó "
     "poco antes de 1577, y en 1591 llegó la colonia tlaxcalteca"),
    ("Monterrey", 1596, "Tercera fundación, el 20 de septiembre de 1596; las "
     "dos anteriores, de 1577 y 1582, no se sostuvieron"),
    ("Santa Fe", 1610, "Fundada por Pedro de Peralta en 1607 o 1610, según la "
     "fuente; en 1610 quedó de capital"),
    ("El Paso del Norte", 1659, "8 de diciembre de 1659"),
    ("Monclova", 1689, "12 de agosto de 1689, después de un siglo de intentos"),
    ("Loreto", 1697, "25 de octubre de 1697; fue capital de las Californias "
     "hasta 1777"),
    ("Albuquerque", 1706, "Solo consta el año"),
    ("Chihuahua", 1709, "Real de minas el 12 de octubre de 1709"),
    ("San Antonio", 1718, "Misión y presidio en mayo de 1718; la villa de San "
     "Fernando, con isleños canarios, en 1731"),
    ("Laredo", 1755, "El día se discute: el 25 de agosto según unas fuentes"),
    ("San Diego", 1769, "Presidio el 14 de mayo y misión el 16 de julio"),
    ("Monterey", 1770, "Presidio y misión el 3 de junio de 1770"),
    ("Tucson", 1775, "Presidio de San Agustín, 20 de agosto de 1775; la misión "
     "de San Xavier del Bac es de 1700"),
    ("San Francisco", 1776, "Presidio el 17 de septiembre y misión el 9 de "
     "octubre; Anza escogió el sitio en marzo"),
    ("Los Ángeles", 1781, "4 de septiembre de 1781, con cuarenta y cuatro "
     "pobladores llegados de Sonora"),
    ("Santa Bárbara de la Alta California", 1782, "Presidio el 21 de abril de "
     "1782; la misión, en 1786"),
]

# ------------------------------------------------------------- los sucesos
# año, título, qué pasó
SUCESOS = [
    (1519, "Llega la armada", "Cortés desembarca frente a Chalchihuecan el 21 "
     "de abril y en noviembre entra a México-Tenochtitlan"),
    (1520, "La Noche Triste", "La noche del 30 de junio los españoles salen "
     "huyendo de la ciudad"),
    (1521, "Cae Tenochtitlan", "El 13 de agosto termina el sitio y con él el "
     "señorío mexica"),
    (1535, "El virreinato", "Se instala el virreinato de la Nueva España, con "
     "Antonio de Mendoza"),
    (1546, "La plata", "El hallazgo de Zacatecas abre el camino de tierra "
     "adentro y con él el norte"),
    (1598, "Nuevo México", "Oñate cruza el río del Norte y funda la primera "
     "villa del Nuevo México"),
    (1680, "La rebelión pueblo", "Los pueblos echan a los españoles del Nuevo "
     "México y gobiernan hasta 1692"),
    (1769, "Las Californias", "La expedición de Portolá y Serra sube a la "
     "Alta California"),
    (1819, "La línea de Adams y Onís", "España y Estados Unidos fijan el "
     "límite: el Sabina, el paralelo 42 y el Pacífico"),
    (1821, "La independencia", "Los Tratados de Córdoba, del 24 de agosto, "
     "cierran tres siglos de virreinato"),
    (1823, "Centroamérica se va", "El 1 de julio las provincias del centro se "
     "declaran independientes de España y de México"),
    (1824, "La federación", "La Constitución del 4 de octubre reparte el país "
     "en diecinueve estados y cuatro territorios"),
    (1836, "Texas se separa", "Después de San Jacinto, Texas se declara "
     "república; México no la reconoce"),
    (1848, "Guadalupe Hidalgo", "El tratado del 2 de febrero cede más de un "
     "millón trescientos mil kilómetros cuadrados"),
    (1853, "La Mesilla", "El tratado del 30 de diciembre vende otros setenta y "
     "seis mil ochocientos kilómetros cuadrados y cierra la frontera de hoy"),
]

# ------------------------------------------- las entidades de 1824, armadas
# nombre, clase, estados de México de hoy, estados de Estados Unidos de hoy.
# Los nombres de los estados mexicanos van sin acento donde así vienen en el
# archivo de geometría, que se armó de los arcos de la WDBII.
ENTIDADES_1824 = [
    ("Chiapas", "estado", ["Chiapas"], []),
    ("Chihuahua", "estado", ["Chihuahua"], []),
    ("Coahuila y Tejas", "estado", ["Coahuila"], ["TX"]),
    ("Durango", "estado", ["Durango"], []),
    ("Guanajuato", "estado", ["Guanajuato"], []),
    ("México", "estado", ["Mexico", "Hidalgo", "Morelos", "Guerrero"], []),
    ("Michoacán", "estado", ["Michoacan"], []),
    ("Nuevo León", "estado", ["Nuevo Leon"], []),
    ("Oajaca", "estado", ["Oaxaca"], []),
    ("Puebla de los Ángeles", "estado", ["Puebla"], []),
    ("Querétaro", "estado", ["Queretaro"], []),
    ("San Luis Potosí", "estado", ["San Luis Potosi"], []),
    ("Sonora y Sinaloa", "estado", ["Sonora", "Sinaloa"], []),
    ("Tabasco", "estado", ["Tabasco"], []),
    ("Tamaulipas", "estado", ["Tamaulipas"], []),
    ("Veracruz", "estado", ["Veracruz"], []),
    ("Xalisco", "estado", ["Jalisco", "Nayarit"], []),
    ("Yucatán", "estado", ["Yucatan", "Campeche", "Quintana Roo"], []),
    ("Zacatecas", "estado", ["Zacatecas", "Aguascalientes"], []),
    ("Alta California", "territorio", [], ["CA", "NV", "UT", "AZ"]),
    ("Baja California", "territorio",
     ["Baja California", "Baja California Sur"], []),
    ("Colima", "territorio", ["Colima"], []),
    ("Santa Fe de Nuevo México", "territorio", [], ["NM", "CO"]),
    ("Tlaxcala", "territorio", ["Tlaxcala"], []),
    ("Distrito Federal", "distrito", ["Ciudad de Mexico"], []),
]

# Lo que se fue, y cuándo. Los estados de hoy sirven de molde.
PERDIDO = [
    (1836, "República de Texas", [], ["TX"],
     "Texas se declara independiente en 1836; México no lo reconoce hasta el "
     "tratado de 1848"),
    (1848, "Cesión de Guadalupe Hidalgo", [], ["CA", "NV", "UT", "AZ", "NM", "CO"],
     "Un millón trescientos sesenta mil kilómetros cuadrados, contando lo que "
     "ya reclamaba Texas"),
]

# La línea de Adams y Onís, artículo 3 del tratado de 1819, punto por punto.
LINEA_1819 = [
    (29.6800, -93.8400), (31.0000, -93.7500), (32.0000, -93.8300),
    (32.0000, -94.0400), (33.5600, -94.0400), (34.4000, -99.3000),
    (35.0000, -100.0000), (36.5000, -100.0000), (37.5000, -100.0000),
    (38.0700, -102.6200), (38.5000, -105.0000), (39.1000, -106.3000),
    (42.0000, -106.3000), (42.0000, -124.2000),
]
LINEA_1819_NOTA = ("Del Sabina al paralelo 32, de ahí al río Rojo, al "
                   "meridiano 100, al Arkansas y su nacimiento, y por el "
                   "paralelo 42 hasta el Pacífico")

# La frontera de 1848: el Bravo, el Gila y el mar. Trazo simplificado.
LINEA_1848 = [
    (25.9500, -97.1500), (26.4000, -99.0000), (29.3000, -100.8000),
    (29.8000, -102.4000), (29.5000, -104.4000), (31.7800, -106.5300),
    (31.7800, -108.2000), (32.7000, -109.5000), (32.7200, -114.7200),
    (32.5300, -117.1200),
]
# La de 1853, la de hoy: el mismo Bravo, luego la Mesilla.
LINEA_1853 = [
    (25.9500, -97.1500), (26.4000, -99.0000), (29.3000, -100.8000),
    (29.8000, -102.4000), (29.5000, -104.4000), (31.7800, -106.5300),
    (31.7800, -108.2000), (31.3300, -108.2000), (31.3300, -111.0700),
    (31.8700, -114.8100), (32.5300, -117.1200),
]

FUENTES = [
    ("Constitución Federal de los Estados Unidos Mexicanos de 1824",
     "https://archivos.juridicas.unam.mx/www/legislacion/federal/historicos/1824.pdf"),
    ("Adams-Onís Treaty", "https://en.wikipedia.org/wiki/Adams%E2%80%93On%C3%ADs_Treaty"),
    ("Tratado de Guadalupe Hidalgo",
     "https://en.wikipedia.org/wiki/Treaty_of_Guadalupe_Hidalgo"),
    ("Gadsden Purchase", "https://en.wikipedia.org/wiki/Gadsden_Purchase"),
    ("Conquista de México", "https://es.wikipedia.org/wiki/Conquista_de_M%C3%A9xico"),
]

# nombre corto para el mapa, donde el largo no cabe
CORTO = {
    "Santa Bárbara de la Alta California": "Santa Bárbara",
    "México-Tenochtitlan": "Tenochtitlan",
    "El Paso del Norte": "El Paso",
    "Santa Fe de Nuevo México": "Nuevo México",
    "Puebla de los Ángeles": "Puebla",
    "Distrito Federal": "D. F.",
}

AÑO_INICIO, AÑO_FIN = 1519, 1853
