# Guia de Setup — Sistema de Gestão Escolar (PI)

Este guia parte do zero: assume que você nunca usou Git nem configurou um projeto Django antes. Siga os passos **na ordem**, sem pular nenhum. Onde houver comando de terminal, copie e cole exatamente como está — atenção a maiúsculas/minúsculas e espaços.

Todos os comandos abaixo são para **Windows**, usando o **PowerShell**.

---

## 1. Instalar o Git

1. Verifique se já está instalado. Abra o PowerShell (menu Iniciar → digite "PowerShell" → abra "Windows PowerShell") e digite:
   ```powershell
   git --version
   ```
2. Se aparecer uma versão (ex: `git version 2.54.0`), pule para a seção 2.
3. Se der erro, baixe em: https://git-scm.com/download/win
4. Execute o instalador, pode deixar todas as opções no padrão (clicar "Next" em tudo).
5. **Feche e abra o PowerShell de novo** depois de instalar, e teste `git --version` outra vez.

---

## 2. Instalar o Python

1. Verifique se já está instalado:
   ```powershell
   python --version
   ```
2. Se aparecer uma versão 3.11 ou superior, pule para a seção 3.
3. Se der erro, baixe em: https://www.python.org/downloads/
4. **Atenção — passo crítico:** na primeira tela do instalador, marque a caixinha **"Add python.exe to PATH"** antes de clicar em "Install Now". Esquecer isso é a causa mais comum de erro depois.
5. Feche e abra o PowerShell de novo, teste `python --version`.

> **Se mesmo assim `python --version` der erro** ("não pode encontrar o caminho especificado"), tente:
> ```powershell
> py --version
> ```
> Se isso funcionar, o Python está instalado mas só acessível pelo comando `py`. Nesse caso, troque `python` por `py` **apenas** no comando de criar o ambiente virtual (seção 5) — depois de ativado, `python` volta a funcionar normalmente.

---

## 3. Configurar sua identidade no Git

Isso só precisa ser feito **uma vez por computador**. Use seu nome e o e-mail da sua conta GitHub:

```powershell
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
```

---

## 4. Clonar o repositório

1. Escolha uma pasta local no seu computador, **fora de qualquer pasta sincronizada por OneDrive, Google Drive ou Dropbox**. Sincronização automática de nuvem conflita com o Git e pode corromper o projeto.

   Para verificar se uma pasta está sincronizada, veja se o caminho contém "OneDrive" (ex: `C:\Users\voce\OneDrive\Documentos` = sincronizada; `C:\Users\voce\Documents` = local, segura).

2. No PowerShell, navegue até onde quer guardar o projeto e clone:

   ```powershell
   cd C:\Users\SeuUsuario\Documents
   mkdir ProjetoIntegrador
   cd ProjetoIntegrador
   git clone https://github.com/AssumFeres/gestao-escolar.git
   cd gestao-escolar
   ```

3. Troque para a branch de desenvolvimento (é onde o trabalho do dia a dia acontece — nunca trabalhamos direto na `main`):

   ```powershell
   git checkout dev
   ```

---

## 5. Criar e ativar o ambiente virtual

O ambiente virtual isola as bibliotecas Python deste projeto do resto do seu computador. **Cada pessoa cria o seu próprio**, ele nunca é compartilhado pelo Git.

```powershell
python -m venv venv
```

(Se `python` não funcionar nessa máquina, use `py -m venv venv` — veja a observação na seção 2.)

Ativar:

```powershell
.\venv\Scripts\Activate.ps1
```

Se aparecer `(venv)` no início da linha do terminal, funcionou. Pule para a seção 6.

### Se aparecer erro de "execução de scripts desabilitada"

É uma proteção padrão do Windows, resolve com um comando (só precisa rodar uma vez por computador):

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Confirme digitando `S` e Enter quando perguntado. Depois, tente ativar de novo:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 6. Instalar as dependências do projeto

Com `(venv)` aparecendo no início da linha (ambiente ativado), rode:

```powershell
pip install -r requirements.txt
```

Isso instala Django e todas as bibliotecas que o projeto usa. Pode levar um ou dois minutos.

---

## 7. Criar o banco de dados local e seu usuário

O banco de dados **não vem pelo Git** — cada computador cria o seu próprio, localmente:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

O `createsuperuser` vai pedir um nome de usuário, e-mail (pode deixar em branco, aperte Enter) e senha (a senha não aparece enquanto você digita, é normal).

---

## 8. Rodar o projeto

```powershell
python manage.py runserver
```

Abra o navegador em: **http://127.0.0.1:8000/admin/**

Faça login com o usuário que você acabou de criar. Se aparecer o painel administrativo com as seções do sistema, está tudo funcionando.

Para parar o servidor, `Ctrl+C` no terminal.

---

## 9. Rotina de trabalho do dia a dia

Sempre que for trabalhar no projeto, **nessa ordem**:

### Ao começar (sempre, mesmo que tenha trabalhado ontem na mesma máquina):

```powershell
cd C:\Users\SeuUsuario\Documents\ProjetoIntegrador\gestao-escolar
.\venv\Scripts\Activate.ps1
git checkout dev
git pull origin dev
```

Isso garante que você está com a versão mais recente do código, feita por qualquer pessoa do grupo.

### Durante o trabalho

Se instalou alguma biblioteca nova:
```powershell
pip freeze > requirements.txt
```

### Ao terminar (ou em qualquer ponto que queira salvar progresso):

```powershell
git add .
git status
```

Confira a lista antes de commitar — **nunca deve aparecer** `venv/`, `db.sqlite3` ou `.env` na lista (se aparecer, avise o grupo, algo está errado com o `.gitignore`).

```powershell
git commit -m "feat: descreva brevemente o que voce fez"
git push
```

Prefixos de commit usados no projeto: `feat` (funcionalidade nova), `fix` (correção de bug), `test` (testes), `docs` (documentação), `chore` (tarefas de configuração/manutenção).

---

## 10. Branches — como trabalhar sem atropelar o código dos outros

- `main` — versão estável, ninguém commita direto aqui.
- `dev` — integração do time.
- `feature/nome-da-tarefa` — sua branch pessoal para uma tarefa específica.

Para começar uma tarefa nova:

```powershell
git checkout dev
git pull origin dev
git checkout -b feature/nome-da-sua-tarefa
```

Trabalhe, commite normalmente nessa branch. Ao terminar, envie e abra um **Pull Request** no GitHub (branch `feature/...` → `dev`) para o grupo revisar antes do merge — não faça merge direto sem avisar o grupo.

```powershell
git push -u origin feature/nome-da-sua-tarefa
```

---

## Erros comuns e soluções rápidas

| Erro | Causa provável | Solução |
|---|---|---|
| `git não é reconhecido...` | Git não instalado ou terminal não foi reaberto após instalar | Reinstalar/reabrir terminal (seção 1) |
| `python não é reconhecido...` | Python não instalado, ou instalado sem marcar "Add to PATH" | Reinstalar marcando a opção, ou usar `py` no lugar de `python` |
| `execução de scripts foi desabilitada` | Política de segurança do PowerShell | Rodar o `Set-ExecutionPolicy` da seção 5 |
| `Author identity unknown` no commit | Git sem nome/e-mail configurado nessa máquina | Rodar os comandos da seção 3 |
| `git commit -m` dá erro de "pathspec" | Espaço extra entre `-` e `m` (ex: `- m` em vez de `-m`) | Digitar `-m` sem espaço |
| `git status` diz "up to date" mas falta arquivo novo | `git status` só compara com a última vez que essa máquina conversou com o GitHub | Rodar `git fetch origin` e depois `git pull origin dev` |
| App novo não aparece no Django | Esqueceu de registrar em `INSTALLED_APPS` no `config/settings.py` | Adicionar o nome do app na lista e rodar `python manage.py check` |

---

## Em caso de dúvida

Não force sozinho por muito tempo — chame o grupo. A maioria dos erros de setup já foi vista e resolvida por alguém antes; é mais rápido perguntar do que tentar adivinhar.
