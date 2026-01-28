> DevOps Praktikum Dokumentacija
---
# Dostava Hrane za restoran Zlatni Čips
Web aplikacija za izmišljeni restoran Zlatni Čips, na kojoj je moguće odabrati stavke s menija i naručiti ih te pratiti stanje svoje narudžbe i procijenjeno vrijeme dostave. Admin može prihvatiti ili odbiti narudžbu ovisno o realnoj situaciji u restoranu i dostupnosti sastojaka. 

---

## Tehnologije

| Komponenta | Tehnologija |
|------------|-------------|
| Frontend | Vue.js 3, TypeScript, Vite |
| Backend | Flask (Python), Gunicorn |
| Baza podataka | Google Firestore |
| Kontejnerizacija | Docker |
| Cloud | AWS (EC2, S3) |

---

## Povezivanje Frontenda s Backendom

Frontend (Vue.js) na portu 5173 koji se spaja na backend (Flask) na portu 3000

### Konfiguracija API URL-a

Frontend koristi environment varijablu `VITE_API_URL` za komunikaciju s backendom.

**Lokalni razvoj** (`frontend-vue/.env`):
```
VITE_API_URL=http://localhost:3000
```

**Produkcija** (`frontend-vue/.env.production`):
```
VITE_API_URL=http://<EC2_PUBLIC_IP>:3000
```

### API Pozivi u Frontendu

Frontend dohvaća API URL iz environment varijable:

```typescript
const API = import.meta.env.VITE_API_URL;

// Primjer: Dohvat menija
const response = await fetch(`${API}/meni`);
const menuItems = await response.json();

// Primjer: Kreiranje narudžbe
const response = await fetch(`${API}/narudba`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, items, total_price })
});
```

### Backend API Endpointi

| Metoda | Endpoint | Opis |
|--------|----------|------|
| GET | `/` | Health check |
| GET | `/meni` | Dohvat svih stavki menija |
| POST | `/narudba` | Kreiranje nove narudžbe |
| GET | `/narudba/<broj>` | Dohvat pojedine narudžbe |
| GET | `/user-orders/<username>` | Narudžbe korisnika |
| GET | `/all-orders` | Sve narudžbe (admin) |
| PATCH | `/narudba/<broj>/status` | Promjena statusa narudžbe |
| POST | `/signup` | Registracija korisnika |
| POST | `/login` | Prijava korisnika |

### CORS Konfiguracija

Backend omogućuje CORS za komunikaciju s frontendom:

```python
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
```

---

## Deployment na AWS

### Preduvjeti

1. AWS račun s konfiguriranima pristupnim ključevima
2. AWS CLI instaliran i konfiguriran
3. Firebase AccountKey.json datoteka

```powershell
# Konfiguracija AWS CLI
aws configure
# Unijeti: Access Key ID, Secret Access Key, Region (us-east-1)
```

---

### 1. Backend Deployment (EC2)

#### 1.1 Kreiranje Security Group

Security group definira pravila vatrozida za EC2 instancu.

```powershell
# Kreiranje security grupe
aws ec2 create-security-group --group-name flask-backend-sg --description "Security group for Flask backend"

# Dodavanje pravila za SSH (port 22)
aws ec2 authorize-security-group-ingress --group-name flask-backend-sg --protocol tcp --port 22 --cidr 0.0.0.0/0

# Dodavanje pravila za HTTP (port 80)
aws ec2 authorize-security-group-ingress --group-name flask-backend-sg --protocol tcp --port 80 --cidr 0.0.0.0/0

# Dodavanje pravila za HTTPS (port 443)
aws ec2 authorize-security-group-ingress --group-name flask-backend-sg --protocol tcp --port 443 --cidr 0.0.0.0/0

# Dodavanje pravila za Flask (port 3000)
aws ec2 authorize-security-group-ingress --group-name flask-backend-sg --protocol tcp --port 3000 --cidr 0.0.0.0/0
```

#### 1.2 Kreiranje SSH Ključa

```powershell
aws ec2 create-key-pair --key-name flask-backend-key --query "KeyMaterial" --output text | Out-File -Encoding ascii flask-backend-key.pem
```

#### 1.3 Pokretanje EC2 Instance

```powershell
aws ec2 run-instances --image-id ami-0c02fb55956c7d316 --instance-type t3.micro --key-name flask-backend-key --security-group-ids <SECURITY_GROUP_ID> --associate-public-ip-address --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=flask-backend}]"
```

#### 1.4 Dohvat Javne IP Adrese

```powershell
aws ec2 describe-instances --filters "Name=tag:Name,Values=flask-backend" --query "Reservations[0].Instances[0].PublicIpAddress" --output text
```

#### 1.5 Postavljanje Dozvola za Ključ (Windows)

```powershell
icacls flask-backend-key.pem /reset
icacls flask-backend-key.pem /inheritance:r
icacls flask-backend-key.pem /grant:r "$($env:USERNAME):(R)"
```

#### 1.6 Spajanje na EC2 putem SSH

```powershell
ssh -i flask-backend-key.pem ec2-user@<EC2_PUBLIC_IP>
```

#### 1.7 Instalacija Dockera na EC2

Izvršiti na EC2 instanci:

```bash
# Ažuriranje sustava
sudo yum update -y

# Instalacija Dockera
sudo yum install -y docker

# Pokretanje Docker servisa
sudo systemctl start docker
sudo systemctl enable docker

# Dodavanje korisnika u docker grupu
sudo usermod -a -G docker ec2-user

# Odjaviti se i ponovno prijaviti
exit
```

#### 1.8 Prijenos Backend Datoteka

Kreiranje direktorija na EC2:
```bash
mkdir -p ~/flask-app
```

Prijenos s lokalnog računala (PowerShell):
```powershell
# Prijenos backend koda
scp -i flask-backend-key.pem -r backend/* ec2-user@<EC2_PUBLIC_IP>:~/flask-app/

# Prijenos Firebase credentials
scp -i flask-backend-key.pem path\to\AccountKey.json ec2-user@<EC2_PUBLIC_IP>:~/flask-app/
```

#### 1.9 Build i Pokretanje Docker Kontejnera

Na EC2 instanci:

```bash
cd ~/flask-app

# Docker slika
docker build -t flask-backend .

# Pokretanje kontejnera
docker run -d --name flask-app --restart always -p 3000:3000 -v $(pwd)/AccountKey.json:/secrets/AccountKey.json:ro flask-backend

# Provjera statusa
docker ps
docker logs flask-app
```

#### 1.10 Testiranje Backenda

```bash
curl http://localhost:3000/
```

Ili u pregledniku: `http://<EC2_PUBLIC_IP>:3000/`

---

### 2. Frontend Deployment (S3)

#### 2.1 Kreiranje S3 Bucketa

```powershell
aws s3 mb s3://devops-praktikum-frontend --region us-east-1
```

#### 2.2 Konfiguracija Static Website Hostinga

```powershell
aws s3 website s3://devops-praktikum-frontend --index-document index.html --error-document index.html
```

#### 2.3 Omogućavanje Javnog Pristupa

```powershell
# Onemogućavanje blokiranja javnog pristupa
aws s3api put-public-access-block --bucket devops-praktikum-frontend --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# Postavljanje bucket policy za javno čitanje
aws s3api put-bucket-policy --bucket devops-praktikum-frontend --policy '{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"PublicReadGetObject\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::devops-praktikum-frontend/*\"}]}'
```

#### 2.4 Build Frontenda za Produkciju

```powershell
cd frontend-vue

# Postavljanje produkcijskog API URL-a
echo "VITE_API_URL=http://<EC2_PUBLIC_IP>:3000" | Out-File -Encoding utf8 .env.production

# Build za produkciju
npm run build
```

#### 2.5 Upload na S3

```powershell
aws s3 sync dist/ s3://devops-praktikum-frontend --delete
```

#### 2.6 Pristup Aplikaciji

Frontend je dostupan na:
```
http://devops-praktikum-frontend.s3-website-us-east-1.amazonaws.com
```

---

## Greške i Rješenja

| Greška | Uzrok | Rješenje |
|--------|-------|----------|
| `t2.micro` nije free tier | Ovisi o regiji | Koristiti `t3.micro` |
| SSH connection timeout | Security grupa u krivom VPC-u | Kreirati SG u istom VPC-u ili koristiti `--security-group-ids` |
| Bad permissions na .pem | Windows dozvole | Koristiti `icacls` za ograničavanje pristupa |
| `IsADirectoryError` za AccountKey.json | Docker kreira direktorij kad datoteka ne postoji | Obrisati direktorij, kopirati pravu datoteku, restartati kontejner |
| TypeScript greške (unused variables) | Striktna TS provjera | Obrisati nekorištene funkcije |

---

## Korisne Naredbe

```powershell
# Provjera statusa EC2 instance
aws ec2 describe-instances --filters "Name=tag:Name,Values=flask-backend" --query "Reservations[0].Instances[0].[State.Name,PublicIpAddress]" --output text

# SSH na EC2
ssh -i flask-backend-key.pem ec2-user@<IP>

# Pregled Docker logova
docker logs flask-app

# Restart kontejnera
docker restart flask-app

# Ponovna objava frontenda
npm run build
aws s3 sync dist/ s3://devops-praktikum-frontend --delete

# Brisanje EC2 instance (čišćenje)
aws ec2 terminate-instances --instance-ids <INSTANCE_ID>

# Brisanje S3 bucketa (čišćenje)
aws s3 rb s3://devops-praktikum-frontend --force
```
