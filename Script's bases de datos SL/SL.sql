DROP TABLE Actuaciones CASCADE CONSTRAINTS;
DROP TABLE Telefonos_abogados CASCADE CONSTRAINTS;
DROP TABLE Telefonos_empresa CASCADE CONSTRAINTS;
DROP TABLE Telefonos_clientes CASCADE CONSTRAINTS;
DROP TABLE Expedientes CASCADE CONSTRAINTS;
DROP TABLE Estados CASCADE CONSTRAINTS;
DROP TABLE Etapas CASCADE CONSTRAINTS;
DROP TABLE Abogados CASCADE CONSTRAINTS;
DROP TABLE Clientes CASCADE CONSTRAINTS;
DROP TABLE Empresa CASCADE CONSTRAINTS;

CREATE TABLE Empresa (
    id_empresa INTEGER PRIMARY KEY,
    nombre_empresa VARCHAR2(50),
    RFC_empresa VARCHAR2(20),
    direccion VARCHAR2(100)
);

CREATE TABLE Clientes (
    id_cliente INTEGER PRIMARY KEY,
    nombre VARCHAR2(50),
    correo VARCHAR2(50),
    RFC VARCHAR2(20)
);

CREATE TABLE Abogados (
    id_abogado INTEGER PRIMARY KEY,
    nombre_abogado VARCHAR2(50),
    correo VARCHAR2(50)
);

CREATE TABLE Etapas (
    id_etapa INTEGER PRIMARY KEY,
    nombre_etapa VARCHAR2(50),
    descripcion VARCHAR2(100)
);

CREATE TABLE Estados (
    id_estado INTEGER PRIMARY KEY,
    nombre_estado VARCHAR2(50)
);

CREATE TABLE Expedientes (
    id_expedientes INTEGER PRIMARY KEY,
    numero_expediente VARCHAR2(20),
    fecha_inicio DATE,
    id_cliente INTEGER,
    id_empresa INTEGER, -- empresa demandada
    id_abogado INTEGER,
    id_etapa INTEGER,
    id_estado INTEGER,
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente),
    FOREIGN KEY (id_empresa) REFERENCES Empresa(id_empresa),
    FOREIGN KEY (id_abogado) REFERENCES Abogados(id_abogado),
    FOREIGN KEY (id_etapa) REFERENCES Etapas(id_etapa),
    FOREIGN KEY (id_estado) REFERENCES Estados(id_estado)
);

CREATE TABLE Historial_etapas (
    id_historial INTEGER PRIMARY KEY,
    fecha_inicio DATE,
    fecha_fin DATE,
    id_expedientes INTEGER,
    id_etapa INTEGER,
    FOREIGN KEY (id_expedientes) REFERENCES Expedientes(id_expedientes),
    FOREIGN KEY (id_etapa) REFERENCES Etapas(id_etapa)
);

CREATE TABLE Telefonos_abogados (
    id_telefono INTEGER PRIMARY KEY,
    telefono VARCHAR2(15),
    id_abogado INTEGER,
    FOREIGN KEY (id_abogado) REFERENCES Abogados(id_abogado)
);

CREATE TABLE Telefonos_empresa (
    id_telefono INTEGER PRIMARY KEY,
    telefono VARCHAR2(15),
    id_empresa INTEGER,
    FOREIGN KEY (id_empresa) REFERENCES Empresa(id_empresa)
);

CREATE TABLE Telefonos_clientes (
    id_telefono INTEGER PRIMARY KEY,
    telefono VARCHAR2(15),
    id_cliente INTEGER,
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente)
);

CREATE TABLE Actuaciones (
    id_evento INTEGER,
    id_expedientes INTEGER,
    tipo_evento VARCHAR2(30),
    descripcion VARCHAR2(100),
    fecha_evento DATE,
    PRIMARY KEY (id_evento, id_expedientes),
    FOREIGN KEY (id_expedientes) REFERENCES Expedientes(id_expedientes)
);

CREATE TABLE Usuarios (
    id INTEGER PRIMARY KEY,
    username VARCHAR2(50),
    password VARCHAR2(20)
);

CREATE SEQUENCE TELEFONOS_CLIENTES_SEQ
START WITH 16
INCREMENT BY 1
NOCACHE;

CREATE SEQUENCE CLIENTES_SEQ
START WITH 16
INCREMENT BY 1
NOCACHE;

CREATE SEQUENCE TELEFONOS_SEQ
START WITH 16
INCREMENT BY 1
NOCACHE;

CREATE SEQUENCE seq_expedientes START WITH 1 INCREMENT BY 1;

CREATE SEQUENCE abogados_seq
START WITH 11
INCREMENT BY 1
NOCACHE
NOCYCLE;