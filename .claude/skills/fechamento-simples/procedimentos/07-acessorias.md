# 07 · Enviar pelo Acessórias

**Objetivo:** entregar as guias ao cliente pelo Acessórias e deixar a obrigação marcada como entregue.

> **Aprovação obrigatória antes de enviar ao cliente** nos níveis 1 e 2.

## Caminho principal: robô e-Contínuo
O **e-Contínuo** do Acessórias lê o PDF da guia e identifica a empresa, a obrigação e a competência pelo conteúdo. Em
seguida ele dá a entrega como feita e avisa o cliente com protocolo.

> **Colocar o arquivo na pasta do e-Contínuo é o mesmo que enviar ao cliente.** A aprovação vem antes de copiar.

1. Depois da aprovação, copie os PDFs de `guias/` para a pasta monitorada pelo e-Contínuo. [MAPEAR] Caminho da pasta
   nesse computador. Outra opção é enviar pela API:
   ```
   python ferramentas/acessorias.py enviar trabalho/<AAAA-MM>/<codigo>/guias/DAS_<codigo>_<AAAA-MM>.pdf --confirmo-envio
   ```
2. Confirme a entrega:
   ```
   python ferramentas/acessorias.py entregas <CNPJ> --de <AAAA-MM-01> --ate <AAAA-MM-DD>
   ```
   Se não quiser usar a API, confirme na tela do Acessórias.
3. Arquivo recusado ("Arquivo não identificado"): pare e avise. O layout precisa ser aprovado pelo suporte do
   Acessórias.

O token da API é gerado no Acessórias em Configurações → API Token. Ele fica na variável de ambiente
`ACESSORIAS_TOKEN` do computador, nunca no repositório.

## Alternativa manual
Anexar pela tela do Acessórias, na obrigação da empresa. [MAPEAR] Caso o e-Contínuo não reconheça algum tipo de guia.

## Quando parar
Empresa ou obrigação não encontrada, arquivo recusado ou envio sem confirmação.
