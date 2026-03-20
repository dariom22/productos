"""Datos de ejemplo para cargar en la base de datos."""

from datetime import date

from sqlalchemy.orm import Session

from app.models.tours import Tour


TOURS_EJEMPLO = [
    {
        "nombre": "Aventura en la Patagonia",
        "destino": "Bariloche, Argentina",
        "descripcion": "Recorrido por los lagos y montañas de la Patagonia argentina. Trekking, kayak y paseos en lancha.",
        "duracion_dias": 7,
        "precio": 1200.0,
        "cupos_disponibles": 15,
        "fecha_salida": date(2026, 5, 15),
        "incluye": "Alojamiento, desayuno, traslados, guía bilingüe, equipo de trekking",
        "categoria": "aventura",
    },
    {
        "nombre": "Maravillas de Machu Picchu",
        "destino": "Cusco, Perú",
        "descripcion": "Visita la ciudadela inca de Machu Picchu, el Valle Sagrado y la ciudad de Cusco.",
        "duracion_dias": 5,
        "precio": 890.0,
        "cupos_disponibles": 20,
        "fecha_salida": date(2026, 6, 1),
        "incluye": "Alojamiento, desayuno y cena, entradas, guía profesional, tren a Machu Picchu",
        "categoria": "cultural",
    },
    {
        "nombre": "Playas del Caribe Mexicano",
        "destino": "Cancún, México",
        "descripcion": "Relax total en las playas de Cancún con excursiones a Chichén Itzá e Isla Mujeres.",
        "duracion_dias": 6,
        "precio": 1050.0,
        "cupos_disponibles": 25,
        "fecha_salida": date(2026, 4, 20),
        "incluye": "Alojamiento all-inclusive, traslados, excursión a Chichén Itzá, snorkel",
        "categoria": "playa",
    },
    {
        "nombre": "Safari en Kenia",
        "destino": "Nairobi, Kenia",
        "descripcion": "Safari por el Masái Mara y el Parque Nacional de Amboseli. Avistamiento de los Big Five.",
        "duracion_dias": 8,
        "precio": 2500.0,
        "cupos_disponibles": 10,
        "fecha_salida": date(2026, 7, 10),
        "incluye": "Alojamiento en lodges, pensión completa, 4x4 con guía, vuelo interno",
        "categoria": "aventura",
    },
    {
        "nombre": "Roma y Toscana",
        "destino": "Roma, Italia",
        "descripcion": "Recorre Roma, Florencia y la campiña toscana. Historia, arte y gastronomía.",
        "duracion_dias": 9,
        "precio": 1800.0,
        "cupos_disponibles": 18,
        "fecha_salida": date(2026, 5, 25),
        "incluye": "Alojamiento, desayuno, traslados, entradas a museos, degustación de vinos",
        "categoria": "cultural",
    },
    {
        "nombre": "Cataratas del Iguazú",
        "destino": "Puerto Iguazú, Argentina",
        "descripcion": "Visitá las Cataratas del Iguazú desde ambos lados (Argentina y Brasil). Incluye paseo en lancha.",
        "duracion_dias": 3,
        "precio": 450.0,
        "cupos_disponibles": 30,
        "fecha_salida": date(2026, 4, 10),
        "incluye": "Alojamiento, desayuno, traslados, entradas, paseo en lancha Gran Aventura",
        "categoria": "naturaleza",
    },
    {
        "nombre": "Río de Janeiro Tropical",
        "destino": "Río de Janeiro, Brasil",
        "descripcion": "Cristo Redentor, Pan de Azúcar, playas de Copacabana e Ipanema, y vida nocturna carioca.",
        "duracion_dias": 5,
        "precio": 780.0,
        "cupos_disponibles": 22,
        "fecha_salida": date(2026, 6, 15),
        "incluye": "Alojamiento, desayuno, traslados, city tour, entrada al Cristo Redentor",
        "categoria": "playa",
    },
    {
        "nombre": "Escapada a Mendoza",
        "destino": "Mendoza, Argentina",
        "descripcion": "Ruta del vino, Alta Montaña y termas. Ideal para parejas y amantes del vino.",
        "duracion_dias": 4,
        "precio": 550.0,
        "cupos_disponibles": 16,
        "fecha_salida": date(2026, 5, 1),
        "incluye": "Alojamiento, desayuno, tour de bodegas, excursión Alta Montaña, degustaciones",
        "categoria": "naturaleza",
    },
]


def seed_database(db: Session):
    """Carga los tours de ejemplo si la base está vacía."""
    existing = db.query(Tour).count()
    if existing > 0:
        return

    for tour_data in TOURS_EJEMPLO:
        db.add(Tour(**tour_data))
    db.commit()
