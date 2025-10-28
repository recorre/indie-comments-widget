# 🚀 Deploy FastAPI Proxy na Vercel

## 📁 Estrutura de Arquivos

```
seu-projeto/
├── api/
│   └── index.py          # FastAPI app (copie o código do proxy)
├── vercel.json           # Configuração Vercel
├── requirements.txt      # Dependências Python
└── .env.example          # Template de variáveis
```

## 🔧 Passo 1: Criar Estrutura

1. **Crie a pasta `api/`**:
```bash
mkdir api
```

2. **Crie `api/index.py`** e cole o código do proxy FastAPI

3. **Crie `requirements.txt`** na raiz (já fornecido)

4. **Crie `vercel.json`** na raiz (já fornecido)

## 🔑 Passo 2: Configurar Variáveis de Ambiente

### Na Vercel Dashboard:

1. Vá em **Settings** → **Environment Variables**
2. Adicione:

```
NOCODEBACKEND_API_KEY = 00f3a27be70f1a64926af9385089c2b4503edabc8c8db66d09f9657f30bb
INSTANCE = 41300_teste
```

### Localmente (criar `.env`):
```bash
NOCODEBACKEND_API_KEY=00f3a27be70f1a64926af9385089c2b4503edabc8c8db66d09f9657f30bb
INSTANCE=41300_teste
```

## 🌐 Passo 3: Deploy

### Opção A - Via Vercel CLI (Recomendado)

1. **Instalar Vercel CLI**:
```bash
npm i -g vercel
```

2. **Login na Vercel**:
```bash
vercel login
```

3. **Deploy**:
```bash
vercel
```

4. **Produção**:
```bash
vercel --prod
```

### Opção B - Via GitHub

1. **Push para GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/seu-usuario/seu-repo.git
git push -u origin main
```

2. **Conectar na Vercel**:
   - Vá em [vercel.com](https://vercel.com)
   - Click **Import Project**
   - Selecione seu repositório
   - Adicione as variáveis de ambiente
   - Click **Deploy**

## ✅ Passo 4: Testar

Após deploy, sua API estará em: `https://seu-projeto.vercel.app`

### Endpoints para testar:

```bash
# Health check
curl https://seu-projeto.vercel.app/health

# Root
curl https://seu-projeto.vercel.app/

# Criar usuário
curl -X POST https://seu-projeto.vercel.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "123456"
  }'

# Buscar comentários
curl https://seu-projeto.vercel.app/comments?thread_id=1
```

## 📚 Endpoints Disponíveis

### 🔐 Autenticação
- `POST /auth/register` - Criar conta
- `POST /auth/login` - Login

### 🧵 Threads
- `POST /threads` - Criar thread
- `GET /threads` - Listar threads
- `GET /threads/{id}` - Buscar thread
- `DELETE /threads/{id}` - Deletar thread

### 💬 Comentários (Público)
- `POST /comments` - Criar comentário
- `GET /comments` - Listar comentários
- `GET /comments/{id}` - Buscar comentário

### 🛡️ Moderação (Auth)
- `PUT /comments/{id}/moderate` - Aprovar/rejeitar
- `DELETE /comments/{id}` - Deletar

### 🎨 Widget
- `GET /widget/comments/{thread_id}` - Comentários aninhados (otimizado)

### 🎪 Demo
- `GET /demo/thread` - Thread pública de demo

## 🐛 Troubleshooting

### Erro: "API_KEY not configured"
- Verifique se adicionou a variável `NOCODEBACKEND_API_KEY` na Vercel

### Erro: "Module not found"
- Rode `vercel dev` localmente para testar
- Verifique se `requirements.txt` está correto

### Erro: "Function timeout"
- Plano gratuito da Vercel tem timeout de 10s
- Otimize queries ou considere upgrade

## 🚀 Próximos Passos

1. ✅ Deploy do proxy → **FEITO**
2. 🎨 Criar widget JavaScript embedável
3. 🖼️ Criar frontend (dashboard)
4. 🎭 Sistema de temas CSS

**Quer que eu crie o widget JavaScript agora?** 🎯
