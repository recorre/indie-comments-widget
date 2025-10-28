# Estrutura de Pastas - Comment Widget Hackathon

```
comment-widget/
│
├── backend/                      # FastAPI Backend + Proxy
│   ├── api/                      # Endpoints organizados
│   │   ├── __init__.py
│   │   ├── index.py                 # Entry point para Vercel
│   │   ├── auth.py                  # Rotas de autenticação
│   │   ├── threads.py               # Rotas de threads
│   │   ├── comments.py              # Rotas de comentários
│   │   ├── moderation.py            # Rotas de moderação
│   │   └── widget.py                # Endpoints públicos do widget
│   │
│   ├── core/                     # Core do sistema
│   │   ├── __init__.py
│   │   ├── config.py                # Configurações (API_KEY, etc)
│   │   ├── security.py              # Hashing, JWT, autenticação
│   │   ├── dependencies.py          # Dependências FastAPI
│   │   └── database.py              # Cliente NoCodeBackend
│   │
│   ├── models/                   # Pydantic Models
│   │   ├── __init__.py
│   │   ├── user.py                  # User schemas
│   │   ├── thread.py                # Thread schemas
│   │   └── comment.py               # Comment schemas
│   │
│   ├── services/                 # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── thread_service.py
│   │   ├── comment_service.py
│   │   └── nocodebackend.py         # Wrapper API NoCodeBackend
│   │
│   ├── utils/                    # Utilitários
│   │   ├── __init__.py
│   │   ├── hash.py                  # Hashing helpers
│   │   ├── validators.py            # Validações customizadas
│   │   └── logger.py                # Logging configurado
│   │
│   ├── .env.example                 # Template de variáveis
│   ├── .env                         # Variáveis locais (git ignore)
│   ├── requirements.txt             # Dependências Python
│   ├── vercel.json                  # Config deploy Vercel
│   └── main.py                      # Entry point local (dev)
│
├── frontend/                     # Frontend Dashboard
│   ├── static/                   # Assets estáticos
│   │   ├── css/
│   │   │   ├── main.css             # CSS principal
│   │   │   ├── dashboard.css        # Dashboard styles
│   │   │   └── themes/              # Temas do widget
│   │   │       ├── default.css
│   │   │       ├── dark.css
│   │   │       ├── minimal.css
│   │   │       ├── ocean.css
│   │   │       └── sunset.css
│   │   │
│   │   ├── js/
│   │   │   ├── main.js              # JS principal
│   │   │   ├── dashboard.js         # Dashboard interativo
│   │   │   └── theme-switcher.js    # Troca de temas
│   │   │
│   │   ├── images/
│   │   │   ├── logo.svg
│   │   │   └── demo/
│   │   │
│   │   └── fonts/                # Fontes customizadas (opcional)
│   │
│   ├── templates/                # Jinja2 Templates
│   │   ├── base.html                # Template base
│   │   ├── index.html               # Landing page + demo
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── dashboard/
│   │   │   ├── home.html            # Dashboard principal
│   │   │   ├── threads.html         # Gerenciar threads
│   │   │   └── comments.html        # Moderar comentários
│   │   └── components/              # Componentes reutilizáveis
│   │       ├── navbar.html
│   │       ├── footer.html
│   │       └── widget_preview.html
│   │
│   ├── routes/                   # Rotas do frontend
│   │   ├── __init__.py
│   │   ├── pages.py                 # Páginas públicas
│   │   └── dashboard.py             # Páginas autenticadas
│   │
│   └── app.py                       # FastAPI app do frontend
│
├── widget/                       # Widget Embedável
│   ├── src/
│   │   ├── widget.js                # Core do widget
│   │   ├── api.js                   # Cliente API
│   │   ├── renderer.js              # Renderização de comentários
│   │   ├── theme-manager.js         # Gerenciamento de temas
│   │   └── utils.js                 # Helpers
│   │
│   ├── dist/                     # Builds de produção
│   │   ├── comment-widget.min.js    # Bundle minificado
│   │   ├── comment-widget.js        # Bundle legível
│   │   └── widget.css               # CSS base do widget
│   │
│   ├── embed.html                   # Exemplo de embed
│   ├── package.json                 # Deps (se usar bundler)
│   └── rollup.config.js             # Config bundler (opcional)
│
├── scripts/                      # Scripts de automação
│   ├── autotester.py                # Tester de API (já criado)
│   ├── setup_database.py            # Script inicial de setup
│   ├── seed_demo_data.py            # Popular dados de demo
│   ├── generate_api_docs.py         # Converter Swagger→MD
│   ├── build_widget.sh              # Build do widget JS
│   └── deploy.sh                    # Deploy automatizado
│
├── docs/                         # Documentação
│   ├── README.md                    # Documentação principal
│   ├── API.md                       # Documentação da API
│   ├── WIDGET_GUIDE.md              # Como usar o widget
│   ├── DEPLOYMENT.md                # Guia de deploy
│   ├── THEMES.md                    # Documentação de temas
│   ├── api_docs.md                  # API NoCodeBackend (gerado)
│   └── HACKATHON_PITCH.md           # Pitch do projeto
│
├── tests/                        # Testes automatizados
│   ├── test_api.py                  # Testes da API
│   ├── test_widget.js               # Testes do widget
│   └── test_integration.py          # Testes de integração
│
├── examples/                     # Exemplos de uso
│   ├── basic_embed.html             # Embed básico
│   ├── advanced_embed.html          # Embed com customização
│   ├── hugo_example/                # Exemplo Hugo
│   ├── pelican_example/             # Exemplo Pelican
│   └── neocities_example/           # Exemplo Neocities
│
├── .gitignore                       # Arquivos ignorados
├── .env.example                     # Template de variáveis
├── README.md                        # README principal
├── LICENSE                          # Licença do projeto
└── requirements.txt                 # Deps Python (root)
```

## Descrição dos Diretórios
