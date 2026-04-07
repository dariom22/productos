"""Datos de ejemplo para cargar en la base de datos."""

from datetime import date
from sqlalchemy.orm import Session

from app.models.tours import Tour, Proveedor


PROVEEDORES = [
    {"nombre": "Patagonia Adventures", "whatsapp": "+5491155550001", "especialidad": "aventura"},
    {"nombre": "Peru Travel Co", "whatsapp": "+51999550002", "especialidad": "cultural"},
    {"nombre": "Caribe Tours MX", "whatsapp": "+5219985550003", "especialidad": "playa"},
    {"nombre": "African Safari Ltd", "whatsapp": "+254700550004", "especialidad": "aventura"},
    {"nombre": "Italia Bella Tours", "whatsapp": "+39335550005", "especialidad": "cultural"},
    {"nombre": "Iguazú Expediciones", "whatsapp": "+5493757550006", "especialidad": "naturaleza"},
    {"nombre": "Rio Tours Brasil", "whatsapp": "+5521995550007", "especialidad": "playa"},
    {"nombre": "Mendoza Wine Tours", "whatsapp": "+5492614550008", "especialidad": "naturaleza"},
]

TOURS = [
    {
        "nombre": "Aventura en la Patagonia",
        "destino": "Bariloche, Argentina",
        "descripcion": "Recorrido por los lagos y montañas de la Patagonia argentina. Trekking, kayak y paseos en lancha.",
        "duracion_dias": 7, "precio_base": 1200.0, "cupos_disponibles": 15,
        "fecha_salida": date(2026, 5, 15),
        "incluye": "Alojamiento, desayuno, traslados, guía bilingüe, equipo de trekking",
        "categoria": "aventura", "proveedor_idx": 0,
    },
    {
        "nombre": "Maravillas de Machu Picchu",
        "destino": "Cusco, Perú",
        "descripcion": "Visita la ciudadela inca de Machu Picchu, el Valle Sagrado y la ciudad de Cusco.",
        "duracion_dias": 5, "precio_base": 890.0, "cupos_disponibles": 20,
        "fecha_salida": date(2026, 6, 1),
        "incluye": "Alojamiento, desayuno y cena, entradas, guía profesional, tren a Machu Picchu",
        "categoria": "cultural", "proveedor_idx": 1,
    },
    {
        "nombre": "Playas del Caribe Mexicano",
        "destino": "Cancún, México",
        "descripcion": "Relax total en las playas de Cancún con excursiones a Chichén Itzá e Isla Mujeres.",
        "duracion_dias": 6, "precio_base": 1050.0, "cupos_disponibles": 25,
        "fecha_salida": date(2026, 4, 20),
        "incluye": "Alojamiento all-inclusive, traslados, excursión a Chichén Itzá, snorkel",
        "categoria": "playa", "proveedor_idx": 2,
    },
    {
        "nombre": "Safari en Kenia",
        "destino": "Nairobi, Kenia",
        "descripcion": "Safari por el Masái Mara y el Parque Nacional de Amboseli. Avistamiento de los Big Five.",
        "duracion_dias": 8, "precio_base": 2500.0, "cupos_disponibles": 10,
        "fecha_salida": date(2026, 7, 10),
        "incluye": "Alojamiento en lodges, pensión completa, 4x4 con guía, vuelo interno",
        "categoria": "aventura", "proveedor_idx": 3,
    },
    {
        "nombre": "Roma y Toscana",
        "destino": "Roma, Italia",
        "descripcion": "Recorre Roma, Florencia y la campiña toscana. Historia, arte y gastronomía.",
        "duracion_dias": 9, "precio_base": 1800.0, "cupos_disponibles": 18,
        "fecha_salida": date(2026, 5, 25),
        "incluye": "Alojamiento, desayuno, traslados, entradas a museos, degustación de vinos",
        "categoria": "cultural", "proveedor_idx": 4,
    },
    {
        "nombre": "Cataratas del Iguazú",
        "destino": "Puerto Iguazú, Argentina",
        "descripcion": "Visitá las Cataratas del Iguazú desde ambos lados (Argentina y Brasil). Incluye paseo en lancha.",
        "duracion_dias": 3, "precio_base": 450.0, "cupos_disponibles": 30,
        "fecha_salida": date(2026, 4, 10),
        "incluye": "Alojamiento, desayuno, traslados, entradas, paseo en lancha Gran Aventura",
        "categoria": "naturaleza", "proveedor_idx": 5,
    },
    {
        "nombre": "Río de Janeiro Tropical",
        "destino": "Río de Janeiro, Brasil",
        "descripcion": "Cristo Redentor, Pan de Azúcar, playas de Copacabana e Ipanema, y vida nocturna carioca.",
        "duracion_dias": 5, "precio_base": 780.0, "cupos_disponibles": 22,
        "fecha_salida": date(2026, 6, 15),
        "incluye": "Alojamiento, desayuno, traslados, city tour, entrada al Cristo Redentor",
        "categoria": "playa", "proveedor_idx": 6,
    },
    {
        "nombre": "Escapada a Mendoza",
        "destino": "Mendoza, Argentina",
        "descripcion": "Ruta del vino, Alta Montaña y termas. Ideal para parejas y amantes del vino.",
        "duracion_dias": 4, "precio_base": 550.0, "cupos_disponibles": 16,
        "fecha_salida": date(2026, 5, 1),
        "incluye": "Alojamiento, desayuno, tour de bodegas, excursión Alta Montaña, degustaciones",
        "categoria": "naturaleza", "proveedor_idx": 7,
    },
]


def seed_database(db: Session):
    """Carga datos de ejemplo si la base está vacía."""
    if db.query(Tour).count() > 0:
        return

    # Crear proveedores
    proveedores = []
    for p in PROVEEDORES:
        prov = Proveedor(**p)
        db.add(prov)
        proveedores.append(prov)
    db.flush()

    # Crear tours asociados a proveedores
    for t in TOURS:
        idx = t.pop("proveedor_idx")
        t["proveedor_id"] = proveedores[idx].id
        db.add(Tour(**t))

    db.commit()
