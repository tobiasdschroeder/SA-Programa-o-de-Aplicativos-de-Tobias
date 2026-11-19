# Interface do Nexo Hospitalar

## Estado da integração

Esta interface é um protótipo HTML/CSS para as capacidades encontradas em
`codigo/`. O Python atual é uma aplicação de terminal: `codigo/app.py` usa
`input()` e `print()` e não define rotas HTTP, API, templates, login, sessão ou
controle de acesso. Portanto, nenhuma página do navegador lê ou altera o SQLite.

## Funcionalidades existentes no Python

`PacienteManager` oferece cadastro, consulta por ID ou CPF, listagem de ativos,
listagem de inativos, atualização, desativação/inativação, exclusão permanente
somente de inativos e verificação de CPF. O cadastro recebe `nome`, `cpf`,
`data_nascimento`, `telefone`, `endereco` e `tipo_sanguineo` (opcional).
Atualizações também aceitam `status`. A resposta de operação contém `sucesso`,
`mensagem` e, quando aplicável, `paciente`; o modelo retorna ID, campos
cadastrais, status e idade calculada.

Os dados são guardados por `SQLitePacienteRepository` em
`~/.sistema_hospitalar/pacientes.sqlite3`, ou no caminho definido por
`PACIENTES_DB_PATH`. O banco não é criptografado. Use somente dados fictícios e
não publique o arquivo.

Após uma exclusão, o gerenciador reutiliza o menor ID positivo livre. A tabela
`transacoes` conserva apenas o número do paciente, então eventos antigos podem
compartilhar esse número com um cadastro posterior. A interface não exibe nem
consulta essa trilha.

## Páginas

- `index.html`: visão geral das operações implementadas, contrato de campos e
  limitações. Não exibe indicadores derivados de cadastros nem dados de pacientes.
- `login.html`: interface de acesso desabilitada e claramente identificada; não
  coleta credenciais porque não existe autenticação no Python.
- `style.css`: estilos compartilhados, navegação responsiva e estados de foco.
- `script.js`: permanece vazio; esta etapa não usa JavaScript.

## Como visualizar

Abra `interface/index.html` diretamente no navegador. A página de acesso pode
ser aberta pelo link “Acesso ao sistema”. Não é necessário iniciar servidor ou
instalar dependências.

## Limitações e próxima integração

Links de navegação funcionam entre seções e páginas estáticas; não há envio de
formulários, filtros de dados, ações CRUD ou consulta web, pois não existem
endpoints reais para atendê-los. A integração futura exige rotas HTTP no Python,
autenticação e autorização, proteção CSRF, tratamento seguro dos erros e revisão
do armazenamento antes de qualquer uso com informações pessoais. Nenhum
endpoint foi inventado nesta etapa. Os arquivos em `banco_de_dados/` continuam
reservados para a futura etapa SQL; a estrutura SQLite atual é inicializada pelo
repositório Python.