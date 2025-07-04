# Empaquetado de DeepSeek CLI para DEB y RPM

Voy a explicarte cómo compilar tu aplicación Python y crear paquetes DEB (Debian/Ubuntu) y RPM (RedHat/CentOS/Fedora) para distribuir tu herramienta.

## 1. Preparación del proyecto

Primero, organiza tu proyecto con esta estructura:

```
deepseek-cli/
├── src/
│   ├── deepseek_cli/
│   │   ├── __init__.py
│   │   ├── main.py         # (todo el código que te proporcioné antes)
│   │   └── config.json     # plantilla de configuración
├── setup.py
├── MANIFEST.in
├── LICENSE
├── README.md
└── packaging/
    ├── debian/
    │   ├── control
    │   ├── rules
    │   ├── changelog
    │   └── install
    └── rpm/
        ├── specfile.spec
        └── deepseek-cli.service
```

## 2. Archivo setup.py

```python
from setuptools import setup, find_packages

setup(
    name="deepseek-cli",
    version="1.0.0",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'seek=deepseek_cli.main:main',
        ],
    },
    install_requires=[
        'requests>=2.25.1',
        'argcomplete>=1.12.3',
    ],
    python_requires='>=3.6',
    author="Tu Nombre",
    author_email="tu@email.com",
    description="CLI para DeepSeek API",
    license="MIT",
    keywords="deepseek cli api",
    url="https://github.com/tuusuario/deepseek-cli",
)
```

## 3. Creación del paquete DEB

### 3.1 Instalar herramientas necesarias

```bash
sudo apt install dh-python debhelper devscripts fakeroot
```

### 3.2 Crear estructura DEBIAN

```bash
mkdir -p packaging/debian
```

### 3.3 Archivo packaging/debian/control

```
Source: deepseek-cli
Section: utils
Priority: optional
Maintainer: Tu Nombre <tu@email.com>
Build-Depends: debhelper (>= 11), dh-python, python3-all, python3-setuptools
Standards-Version: 4.5.0
Homepage: https://github.com/tuusuario/deepseek-cli

Package: deepseek-cli
Architecture: all
Depends: ${python3:Depends}, ${misc:Depends}, python3-requests, python3-argcomplete
Description: CLI para DeepSeek API
 Herramienta de línea de comandos para interactuar con la API de DeepSeek.
```

### 3.4 Archivo packaging/debian/rules

```makefile
#!/usr/bin/make -f

%:
	dh $@ --with python3 --buildsystem=pybuild
```

### 3.5 Archivo packaging/debian/changelog

```
deepseek-cli (1.0.0-1) unstable; urgency=medium

  * Versión inicial del paquete

 -- Tu Nombre <tu@email.com>  Tue, 01 Jan 2024 12:00:00 +0000
```

### 3.6 Construir el paquete DEB

```bash
cd packaging/debian
debuild -us -uc
```

El paquete `.deb` se generará en el directorio padre.

## 4. Creación del paquete RPM

### 4.1 Instalar herramientas necesarias

```bash
sudo dnf install rpm-build rpmdevtools python3-devel
```

### 4.2 Configurar entorno RPM

```bash
rpmdev-setuptree
```

### 4.3 Crear archivo SPEC

`~/rpmbuild/SPECS/deepseek-cli.spec`

```
Name:           deepseek-cli
Version:        1.0.0
Release:        1%{?dist}
Summary:        CLI para DeepSeek API

License:        MIT
URL:            https://github.com/tuusuario/deepseek-cli
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
Requires:       python3-requests python3-argcomplete

%description
Herramienta de línea de comandos para interactuar con la API de DeepSeek.

%prep
%setup -q

%build
python3 setup.py build

%install
python3 setup.py install --root=%{buildroot} --optimize=1

%files
%license LICENSE
%{_bindir}/seek
%{python3_sitelib}/deepseek_cli/

%changelog
* Tue Jan 01 2024 Tu Nombre <tu@email.com> - 1.0.0-1
- Versión inicial
```

### 4.4 Construir el paquete RPM

```bash
cd ~/rpmbuild/SOURCES
tar czvf deepseek-cli-1.0.0.tar.gz -C path/to/deepseek-cli --exclude=.git --exclude=packaging .
cd ~/rpmbuild/SPECS
rpmbuild -ba deepseek-cli.spec
```

El paquete RPM se generará en `~/rpmbuild/RPMS/noarch/`.

## 5. Instalación del paquete

### Para DEB:

```bash
sudo dpkg -i deepseek-cli_1.0.0-1_all.deb
sudo apt-get install -f  # Para resolver dependencias
```

### Para RPM:

```bash
sudo dnf install ./deepseek-cli-1.0.0-1.noarch.rpm
```

## 6. Verificación

```bash
which seek
seek --help
```

## 7. Consideraciones adicionales

1. **Configuración post-instalación**:
   - El archivo de configuración se puede colocar en `/etc/deepseek/seek.json`
   - Usa `sudo seek config --api-key tu_key` para configuración inicial

2. **Actualizaciones**:
   - Incrementa la versión en setup.py y los archivos de control
   - Actualiza el changelog

3. **Dependencias**:
   - Asegúrate de listar todas las dependencias en setup.py y los archivos de control

4. **Sistema de archivos**:
   - Los paquetes instalarán el ejecutable en `/usr/bin/seek`
   - Los módulos Python irán a `/usr/lib/python3.X/site-packages/deepseek_cli/`

Esta metodología te permite distribuir tu herramienta profesionalmente en sistemas basados en Debian y RedHat.
