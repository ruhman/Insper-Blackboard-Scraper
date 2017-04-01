# Insper-Blackboard-Scraper

Esse projeto nasceu como algo que eu pessoalmente precisava. Sei que nos disponibilizam muito conteúdo de qualidade, e queria ter uma maneira de sempre te-lo a disposição. Porém, baixar todos os arquivos do Blackboard seria um processo muito lento. Decidi otimizar 😎

Esse script faz download de todos os arquivos disponíveis, mantendo a estrutura organizacional. Ou seja, uma pasta por matéria e subpastas de acordo com a organização dos professores. Existem alguma otimizações para não repetir arquivos já baixados. Portanto, pode ser rodado conforme o tempo e apenas os arquivos novos serão baixados. Também é possível escolher as extensões de arquvivos de interesse.

## Instalação

Primeiro, é necesário instalar as depenências necessárias:

```
pip install lxml
pip install dryscrape
```
A segunda dependência tende a apresentar erros para instalar. Esse link pode ajudar: https://dryscrape.readthedocs.io/en/latest/installation.html

Depois, basta clonar o repositório:
``` git clone https://github.com/ruhman/Insper-Blackboard-Scraper.git```

E rodar o script:
``` python scraper.py```

Agora os arquivos vão começar a aparecer em pastas **no mesmo diretório** do script.

## Features

1.  As matérias que serão baixadas são as presentes na lista da página inicial do Blackboard:

[foto]

Portanto, basta adicionar ou remover matérias na lista para escolher as baixadas pelo script.

1.  É possivel enviar login e senha como argumentos para evitar digitar repetidamente. Exemplo:
``` python scraper.py joaofb1 123456```
