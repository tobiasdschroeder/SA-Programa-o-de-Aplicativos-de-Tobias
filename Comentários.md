# Devolutiva formativa — Atividade 02 da SA

**Estudante:** Tobias  
**Turma:** Rio Negrinho — Tarde  
**UC:** Programação de Aplicativos  
**Projeto:** Sistema hospitalar  
**Repositório:** https://github.com/tobiasdschroeder/SA-Programa-o-de-Aplicativos-de-Tobias

## Pontos positivos

- Arquitetura Flask organizada em módulos.
- Separação entre rotas, modelos e templates.
- Autenticação de usuários.
- Tratamento de erros.
- Proteção CSRF.
- Testes automatizados.
- Funcionalidades de gerenciamento de pacientes.

## Melhorias realizadas

1. Ambiente limpo documentado com criação de venv e instalação das dependências.
2. Debug limitado ao ambiente de desenvolvimento e cookies configurados para uso seguro.
3. Testes atualizados para CPF fictício, login inválido, duplicidade e CSRF.
4. README atualizado com funcionalidades, execução e dados fictícios.
5. Novas abas documentadas: exclusão permanente, verificação de CPF e meu perfil.

## Testes recomendados e cobertos

- Executar os testes com `pytest` ou `unittest`.
- Testar login válido e inválido.
- Tentar cadastrar paciente ou usuário duplicado.
- Verificar a proteção CSRF com token ausente ou incorreto.
- Demonstrar cadastro, consulta, atualização, desativação e exclusão permanente.

## Dados para demonstração

Durante apresentações, use exclusivamente dados fictícios, como nomes de teste, endereços demonstrativos, telefones fictícios e CPFs formados por sequências como `11111111111`. Não use dados reais de pacientes ou credenciais pessoais.

## Mensagem final

Tobias, seu projeto apresenta organização modular e preocupação com segurança e testes. Continue mantendo a documentação e a execução consistentes.
