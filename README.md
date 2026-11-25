# Da Ideia ao Código: Construção de Aplicações Funcionais

**Curso:** Técnico em Desenvolvimento de Sistemas  
**Unidade curricular:** Programação de Aplicativos  
**Situação de Aprendizagem (SA) nº 1**  
**Material comum às turmas da manhã e da tarde**

## Seu primeiro desafio como desenvolvedor

> Imagine que você acabou de entrar para a equipe de uma empresa de tecnologia.
> A empresa atende clientes de diferentes setores, e cada cliente deseja
> automatizar um processo ou resolver um problema.
>
> Seu papel é **escolher um desses clientes, entender sua necessidade e construir,
> etapa por etapa, um aplicativo funcional**.
> Você não precisa ter um projeto pronto: vamos começar pelo código, aprender a
> criar a interface e depois integrar um banco de dados.

**Escolha somente um projeto entre as dez opções previstas na SA:**

1. Delivery de comida
2. Aplicativo de transporte
3. Loja de departamentos
4. Streaming de vídeo
5. Gerenciamento de estoque
6. Hospital
7. Escola
8. Empresa de Recursos Humanos (RH)
9. Oficina mecânica
10. Fábrica de chocolate

Cada projeto tem particularidades. Pense no que o usuário desse sistema precisa
fazer, qual informação será recebida e qual resultado o aplicativo deve produzir.

Leia a **[Situação de Aprendizagem integral](documentos/SA_INTEGRAL.md)**.
O texto institucional está reproduzido nessa página, separado das orientações do professor.

## Como o projeto será desenvolvido?

| Etapa | Foco | Resultado a demonstrar |
| --- | --- | --- |
| **Bloco 2 — Entrega 1** | Código Python | Uma funcionalidade inicial executável; código-fonte organizado e comentado; testes e explicação da solução. |
| **Etapa de interface** | HTML, CSS e interação | Interface funcional relacionada ao projeto escolhido. |
| **Etapa de banco de dados** | Modelo relacional e SQL | Estrutura do banco e operações de cadastro, consulta, atualização e exclusão, conforme os requisitos. |
| **Etapa integradora** | Aplicação completa | Código, interface e banco integrados; documentação técnica e apresentação. |

**Na avaliação prática B2 será cobrado o código Python, não o HTML/CSS nem o banco de dados.**
As etapas seguintes serão orientadas ao longo das aulas. As datas, critérios
específicos e instrumentos de avaliação serão comunicados pelo professor.

### O que observar na Entrega 1 (B2)?

- Uma funcionalidade inicial adequada ao problema escolhido.
- Organização do código, nomes claros e comentários úteis.
- Aplicação de funções, classes ou módulos, quando apropriado ao problema.
- Execução e capacidade de explicar o que o programa faz.
- Testes e verificação de entradas inválidas, quando aplicável.

Esses itens sintetizam as capacidades do bloco; **não substituem o enunciado
nem os critérios de avaliação comunicados em aula**.

## Estrutura do repositório

```text
.
├── Comentários.md
├── README.md
├── documentos/
│   └── SA_INTEGRAL.md
├── codigo/
│   ├── __init__.py
│   ├── app.py
│   ├── gerenciador.py
│   ├── modelos.py
│   ├── persistencia.py
│   ├── validacoes.py
│   ├── test_app.py
│   └── test_gerenciador.py
├── interface/
│   ├── index.html
│   ├── login.html
│   ├── style.css
│   ├── script.js
│   └── README.md
├── banco_de_dados/
│   ├── estrutura.sql
│   └── crud.sql
└── .gitignore
```

O repositório agora contém uma implementação Python para gerenciamento de
pacientes e um protótipo visual HTML/CSS em `interface/`. O protótipo não se
conecta ao Python: a aplicação existente funciona pelo terminal e ainda não
possui rotas web ou autenticação. Consulte
[a documentação da interface](interface/README.md) para ver o escopo e as
limitações da integração.

- **`codigo/app.py`**: menu e interação pelo terminal.
- **`codigo/gerenciador.py`**: regras de negócio e operações de pacientes.
- **`codigo/modelos.py`** e **`codigo/validacoes.py`**: entidade e regras de validação.
- **`codigo/persistencia.py`**: criação e acesso ao banco SQLite local.
- **`codigo/test_*.py`**: testes automatizados do back-end.
- **`interface/`**: páginas e estilos do protótipo; consulte seu README para
	limitações.
- **`banco_de_dados/`**: espaço reservado para scripts SQL; os arquivos ainda não
	implementam o schema nem operações. O SQLite atual é criado por
	`codigo/persistencia.py`.
- **`documentos/SA_INTEGRAL.md`**: enunciado e capacidades institucionais da SA.

A estrutura é um ponto de partida; o professor orientará possíveis ajustes.

## Execução local atual do sistema Flask

Crie um ambiente virtual limpo e instale as dependências:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Configure a chave secreta e execute apenas em modo de desenvolvimento:

```bash
set FLASK_SECRET_KEY=chave-secreta-ficticia-local
set FLASK_ENV=development
python app.py
```

Em produção, defina uma chave forte por variável de ambiente, use `FLASK_ENV=production` e coloque o aplicativo atrás de um servidor HTTPS. Não use `debug=True` nem publique dados reais.

## Funcionalidades documentadas

- Login e logout com sessão autenticada.
- Primeiro usuário cadastrado por fluxo público; contas posteriores exigem sessão.
- Cadastro, consulta, atualização, listagem e desativação de pacientes.
- Exclusão permanente permitida apenas para pacientes inativos.
- Verificação de CPF cadastrado.
- Aceitação de CPF fictício com 11 dígitos ou formato padrão, sem consulta a bases públicas.
- Proteção CSRF em operações POST, PUT, PATCH e DELETE.
- Senhas armazenadas com hash pelo Werkzeug.

## Testes automatizados

Os testes são isolados por banco temporário e usam somente identificadores, nomes e credenciais fictícios:

```bash
pytest -v
python -m unittest discover -s tests -v
```

A cobertura recomendada inclui login válido e inválido, campos obrigatórios, registro duplicado, token CSRF inválido, CPF fictício, atualização, desativação e exclusão permanente.