# 🎯 Hotmart Overlay System

Sistema completo para detectar novos cadastros de afiliados na Hotmart e exibir animações em tempo real para uso como overlay no OBS Studio.

## 🚀 Características

- ✅ **Detecção automática** de novos afiliados via webhook da Hotmart
- ✅ **Animações chamativas** com confetes e efeitos visuais
- ✅ **Notificações em tempo real** usando Server-Sent Events (SSE)
- ✅ **Interface otimizada** para uso como overlay no OBS
- ✅ **Painel de controle** com estatísticas em tempo real
- ✅ **Sistema de teste** para verificar funcionamento
- ✅ **Configuração simples** e documentação completa

## 📋 Pré-requisitos

- Python 3.11+
- OBS Studio (para usar como overlay)
- Conta na Hotmart com acesso a webhooks

## 🛠️ Instalação

### 1. Clone ou baixe o projeto
```bash
# O projeto já está criado em: /home/ubuntu/hotmart-overlay-system
cd hotmart-overlay-system
```

### 2. Ative o ambiente virtual
```bash
source venv/bin/activate
```

### 3. Instale as dependências (já instaladas)
```bash
pip install -r requirements.txt
```

### 4. Inicie o servidor
```bash
python src/main.py
```

O sistema estará disponível em: `http://localhost:5000`

## 🎥 Configuração no OBS Studio

### Passo 1: Adicionar Fonte Browser
1. No OBS Studio, clique com o botão direito na área de fontes
2. Selecione **"Adicionar" → "Fonte do Navegador"**
3. Dê um nome para a fonte (ex: "Hotmart Overlay")

### Passo 2: Configurar URL
Cole esta URL no campo "URL":
```
http://localhost:5000/
```

### Passo 3: Configurar Dimensões
- **Largura:** 1920px
- **Altura:** 1080px
- **FPS:** 30

### Passo 4: Configurações Avançadas
Marque as opções:
- ☑️ Desligar fonte quando não visível
- ☑️ Atualizar navegador quando a cena se torna ativa
- ☑️ Controlar áudio via OBS

## 🔗 Configuração da Hotmart

### 1. Acesse o painel da Hotmart
Vá para: `https://app-vlc.hotmart.com/tools/webhook`

### 2. Cadastre um novo webhook
- **URL:** `http://SEU_SERVIDOR:5000/webhook/hotmart`
- **Eventos:** Selecione "Compra Aprovada" (PURCHASE_APPROVED)

### 3. Para desenvolvimento local
Use um serviço como ngrok para expor seu servidor local:
```bash
# Instale o ngrok
# Em seguida execute:
ngrok http 5000
```

Use a URL fornecida pelo ngrok no webhook da Hotmart.

## 🧪 Testando o Sistema

### 1. Verificar Status
Acesse: `http://localhost:5000/config.html`

### 2. Teste Manual
```bash
curl -X POST http://localhost:5000/webhook/test
```

### 3. Verificar Logs
O servidor mostrará logs quando novos afiliados forem detectados:
```
🎉 NOVO AFILIADO DETECTADO: Nome do Afiliado (CODIGO123)
```

## 📁 Estrutura do Projeto

```
hotmart-overlay-system/
├── src/
│   ├── models/
│   │   └── user.py          # Modelos do banco de dados
│   ├── routes/
│   │   ├── api.py           # API REST
│   │   ├── webhook.py       # Webhooks da Hotmart
│   │   ├── sse.py           # Server-Sent Events
│   │   └── user.py          # Rotas de usuário
│   ├── static/
│   │   ├── index.html       # Overlay principal
│   │   └── config.html      # Página de configuração
│   ├── database/
│   │   └── app.db           # Banco SQLite
│   └── main.py              # Aplicação principal
├── venv/                    # Ambiente virtual
└── requirements.txt         # Dependências
```

## 🎨 Personalização

### Cores e Estilo
Edite o arquivo `src/static/index.html` para personalizar:
- Cores do gradiente
- Posição das notificações
- Duração das animações
- Efeitos visuais

### Exemplo de personalização:
```css
/* Alterar cores da notificação */
.notification {
    background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
}

/* Alterar posição */
.notification {
    top: 100px;    /* Distância do topo */
    right: 100px;  /* Distância da direita */
}
```

## 📊 API Endpoints

### Webhooks
- `POST /webhook/hotmart` - Recebe webhooks da Hotmart
- `POST /webhook/test` - Teste manual do sistema

### API REST
- `GET /api/stats` - Estatísticas gerais
- `GET /api/new-affiliates` - Novos afiliados pendentes
- `GET /api/affiliates` - Todos os afiliados
- `GET /api/sales` - Vendas recentes

### Server-Sent Events
- `GET /sse/events` - Stream de eventos em tempo real
- `POST /sse/broadcast` - Enviar notificação manual

### Utilitários
- `GET /health` - Status do sistema
- `GET /sse/connections` - Conexões SSE ativas

## 🔧 Solução de Problemas

### Sistema não recebe webhooks
1. Verifique se o servidor está rodando
2. Confirme a URL do webhook na Hotmart
3. Use ngrok para desenvolvimento local
4. Verifique os logs do servidor

### Overlay não aparece no OBS
1. Verifique se a URL está correta
2. Confirme que o servidor está ativo
3. Teste a URL no navegador primeiro
4. Verifique as dimensões configuradas

### Notificações não aparecem
1. Teste com `curl -X POST http://localhost:5000/webhook/test`
2. Verifique o console do navegador (F12)
3. Confirme conexão SSE na página de configuração

## 🚀 Deploy em Produção

Para usar em produção, você pode fazer deploy usando os comandos do sistema:

```bash
# Para frontend (se necessário)
# manus-deploy-frontend

# Para backend
# manus-deploy-backend
```

## 📝 Logs e Monitoramento

O sistema registra automaticamente:
- Novos afiliados detectados
- Webhooks recebidos
- Conexões SSE ativas
- Erros e exceções

## 🤝 Suporte

Para suporte ou dúvidas:
1. Verifique a página de configuração: `http://localhost:5000/config.html`
2. Consulte os logs do servidor
3. Teste os endpoints da API

## 📄 Licença

Este projeto foi criado para uso pessoal/comercial. Sinta-se livre para modificar conforme suas necessidades.

---

**🎉 Pronto! Seu sistema de overlay da Hotmart está funcionando!**

Quando novos afiliados se cadastrarem e fizerem vendas, você verá belas animações com confetes e fogos de artifício no seu stream! 🎊

