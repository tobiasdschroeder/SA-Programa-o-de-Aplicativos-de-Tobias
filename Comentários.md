
# Devolutiva formativa — Atividade 01 da SA

**Estudante:** Tobias  
**Turma:** Rio Negrinho — Tarde  
**Unidade Curricular:** Programação de Aplicativos  
**Projeto:** Sistema Hospitalar — Gerenciamento de Pacientes  
**Código analisado:** `codigo/app.py`  
**Referência:** Situação de Aprendizagem nº 1 — *Da Ideia ao Código*

## O que você já conseguiu desenvolver

Tobias, seu sistema apresenta uma estrutura organizada para o cadastro e gerenciamento de pacientes. Você demonstrou atenção especial às validações, à separação de responsabilidades e à consistência das informações.

Pontos positivos identificados:

- Utilizou as classes `Paciente` e `PacienteManager` para separar o modelo de dados das operações de gerenciamento.
- Criou **funções reutilizáveis de validação** para nome, CPF, data de nascimento, telefone, tipo sanguíneo e situação cadastral.
- Implementou uma verificação dos dígitos do CPF, além de validar seu formato.
- Criou tratamento para datas inválidas e impediu datas de nascimento futuras.
- Implementou cadastro, consulta, listagem, atualização e gerenciamento de pacientes inativos.
- Utilizou **identificadores únicos** para localizar os registros.
- Estruturou o retorno das operações com mensagens padronizadas de sucesso ou falha.
- Organizou o menu com funções específicas e um dicionário de operações.
- Adicionou comentários que descrevem as principais regras do sistema.

## O que precisa ser corrigido

### 1. Planejar a proteção dos dados cadastrados

O programa trabalha com informações como CPF, telefone, endereço e dados relacionados a pacientes.

Embora isso represente um cenário de estudo válido, são informações que exigem cuidado especial em um sistema real.

**Como melhorar:** utilizar somente dados fictícios nos testes, não publicar cadastros reais e planejar mecanismos de autenticação e autorização antes de disponibilizar o sistema para outros usuários.

### 2. Preparar a persistência das informações

Os pacientes são armazenados em uma lista dentro de `PacienteManager`. Ao encerrar o programa, os registros não permanecem disponíveis.

Isso é aceitável para a etapa inicial de programação, mas precisará evoluir quando o projeto integrar um banco de dados.

**Como melhorar:** planejar o armazenamento permanente preservando os identificadores e a situação dos pacientes.

## Oportunidades de melhoria

### 3. Separar as responsabilidades em módulos

O código reúne modelos, validações, gerenciamento e interação pelo terminal em um mesmo arquivo.

**Como melhorar:** considerar módulos específicos para `Paciente`, funções de validação, gerenciamento de registros e interface de terminal. Essa organização facilitará os testes e a manutenção.

### 4. Organizar testes de validação

O projeto contém várias regras importantes, especialmente para CPF, datas e alterações cadastrais.

**Como melhorar:** transformar essas verificações em testes repetíveis, com entradas válidas, inválidas e casos-limite. Dessa forma, futuras alterações poderão ser verificadas sem depender apenas de testes manuais.

### 5. Melhorar a documentação para outros programadores

Os comentários são claros, mas a manutenção será facilitada por uma documentação que explique as regras gerais da aplicação.

**Como melhorar:** complementar o README com instruções de execução, funcionalidades, exemplos de utilização e limitações da versão inicial. Adicionar docstrings às operações mais importantes.

### 6. Planejar o ciclo de vida dos registros

O programa diferencia pacientes ativos e inativos, permitindo também a exclusão de registros inativos.

**Como melhorar:** definir claramente quando um cadastro deve ser inativado, reativado ou excluído e como essas operações serão registradas em uma versão com persistência.

## Testes recomendados

1. Cadastrar um paciente com dados válidos.
2. Tentar cadastrar um CPF inválido ou repetido.
3. Informar uma data de nascimento futura.
4. Testar formatos válidos e inválidos de telefone.
5. Consultar pacientes por identificador e CPF.
6. Atualizar um cadastro com informações válidas e inválidas.
7. Inativar um paciente e conferir as listagens.
8. Tentar excluir um paciente que não atende às regras de exclusão.

## Prioridades para a próxima versão

1. **Documentar os cuidados necessários com dados pessoais.**
2. **Criar testes específicos para as validações.**
3. **Separar o código em módulos.**
4. **Planejar a persistência e o ciclo de vida dos registros.**
5. **Complementar a documentação do projeto.**

## Mensagem final

Tobias, seu código demonstra compreensão de **classes, funções, validação de entradas, estruturas de dados e organização de responsabilidades**. Você apresentou uma solução que procura evitar informações incorretas antes de realizar alterações.

O próximo passo é ampliar a qualidade dos testes, aperfeiçoar a documentação e preparar o projeto para crescer de maneira organizada. **Continue mantendo o cuidado com a consistência dos dados e a clareza das regras de negócio.** Esses são aspectos fundamentais no desenvolvimento de sistemas.
