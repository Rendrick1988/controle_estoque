# Pyright: instalação e uso

Pyright verifica os tipos do Python sem executar o programa. O projeto o mantém como dependência de desenvolvimento do npm; a instalação não adiciona pacotes Python ao `requirements.txt`.

## Pré-requisitos

- Node.js e npm instalados. O pacote Pyright requer Node.js 14 ou superior.
- Dependências Python do projeto instaladas no ambiente virtual `.venv`.

## Instalação

Na raiz do projeto, execute:

```powershell
npm install
```

Esse comando instala a versão registrada no `package-lock.json`. Para instalar ou atualizar Pyright manualmente:

```powershell
npm install --save-dev pyright
```

## Verificar o projeto

Para analisar a aplicação e os testes:

```powershell
npm run typecheck
```

Para analisar somente os testes:

```powershell
npm run typecheck:tests
```

Para verificar um arquivo específico:

```powershell
npx pyright tests/test_internal_security.py
```

A configuração em `pyrightconfig.json` inclui `app/` e `tests/`, exclui arquivos gerados e aponta para `.venv` para resolver as bibliotecas instaladas no ambiente Python do projeto.

## Usar no Visual Studio Code

1. Instale as extensões **Python** e **Pylance** da Microsoft.
2. Abra a paleta de comandos com `Ctrl+Shift+P`.
3. Escolha **Python: Select Interpreter** e selecione `.venv\Scripts\python.exe`.
4. Abra um arquivo `.py`; o Pylance mostrará avisos de tipos no editor.
5. Para confirmar os mesmos arquivos pela linha de comando, execute `npm run typecheck` no terminal integrado.

O Pylance usa o mecanismo de análise de tipos do Pyright e acrescenta recursos próprios do editor. A instalação npm deste projeto fornece o comando de linha de comando; ela não instala nem substitui a extensão Pylance.

## Entender e corrigir avisos

- Leia o tipo esperado no aviso e compare com o valor passado ou retornado.
- Para valores opcionais, trate o caso `None` antes de usar o valor.
- Prefira tipos precisos, como `dict[str, int]`, em vez de `dict[str, object]` quando os dados têm formato conhecido.
- Quando um teste precisa validar dados inválidos de propósito, use uma API de validação que aceite um objeto, como `Model.model_validate({...})`, para que o próprio verificador de tipos não bloqueie o caso.
- Evite silenciar avisos com `Any` ou comentários `type: ignore` sem uma razão específica.

## Links oficiais

- [Instalação do Pyright](https://github.com/microsoft/pyright/blob/main/docs/installation.md)
- [Opções da linha de comando](https://github.com/microsoft/pyright/blob/main/docs/command-line.md)
- [Documentação do Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
