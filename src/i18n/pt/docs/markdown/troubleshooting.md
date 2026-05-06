Troubleshooting Strategies
=====================

Esta página apresenta uma estrutura geral e metódica para resolver por conta própria a maioria dos problemas que você pode encontrar ao usar o Caddy _sem usar IA_. Recomendamos passos semelhantes ao pedir ajuda nos fóruns. Em muitos casos, você consegue responder à própria pergunta ou resolver o próprio problema aplicando algum raciocínio crítico.

O que você sabe?
-----------------

Talvez você não saiba qual é o problema, o que o está causando ou como consertá-lo, então vamos começar com algumas coisas fundamentais que com certeza você sabe:

### O que você espera

Diga isso em voz alta, ou na sua cabeça, ou escreva/digite. Seja claro e específico para que não haja dúvida nem espaço para ambiguidade. Você pode até explicar para si mesmo _por que_ essa é a expectativa.

"Deveria funcionar" não é uma boa expectativa.

"Eu espero um redirecionamento 301 quando fizer uma requisição para este URI" é muito melhor.

### Comportamento atual

Observe o que está acontecendo. O que _exatamente_ está acontecendo e como isso contrasta com a sua expectativa? Sintetize o que você já sabe.

"Não funciona" é inútil e preguiçoso; evite essa frase em todo lugar, exceto talvez como um rótulo resumido para um comportamento específico que já foi documentado em detalhe.

"Em vez de uma resposta 301, estou recebendo uma resposta 200, embora eu veja o cabeçalho `Server: Caddy`" é muito melhor, porque compara e contrasta o que você sabe com o que espera, e sintetiza outras informações conhecidas, o que nos diz que a requisição pelo menos está chegando a uma instância do Caddy.

### Logs

O que há nos logs do Caddy? Por padrão, eles são gravados no terminal que iniciou o processo. Se estiver rodando "desanexado", como um serviço de sistema, talvez você precise buscar os logs em outro lugar.

Observe que logs de requisição HTTP ("access logs") são diferentes dos logs de processo, e precisam ser habilitados explicitamente na sua configuração.

Você também pode querer habilitar logging em nível DEBUG se ainda não o fez.

Mas, de qualquer forma, uma das primeiras coisas que você deve fazer é olhar os logs. _Todos eles._ O contexto da mensagem importa, então uma única linha de log isolada raramente é útil. Colete mais do que você acha que precisa e preserve isso durante o processo de troubleshooting.

Há alguma pista nos logs?

## Reconheça e duvide das suposições

Antes de continuar, precisamos enfatizar o quanto é importante criticar aquilo que você assume. Todos fazemos suposições com base no que estamos acostumados e no que esperamos. "Esteja atento às suas suposições, e grande será o seu poder." (&mdash;Yoda, ou algo assim.)

Por exemplo, uma suposição comum é que, depois de recompilar o Caddy, executar `caddy` fará o novo código rodar. Isso só é verdade se o binário compilado substituir o que está no seu `$PATH`. Caso contrário, `./caddy` costuma ser a invocação correta.

As suposições se acumulam à medida que sua implantação ou configuração fica mais complexa. Por exemplo, implantar em Docker envolve reconstruir uma imagem e executá-la, o que multiplica as suposições que você pode fazer.

Muitas perguntas e relatos de bug acabam sendo problemas em configurações externas de sistema e rede, e não no Caddy em si. Por exemplo, se você não consegue se conectar à sua instância do Caddy, mas o Caddy está claramente em execução, você provavelmente está assumindo que não é DNS. Dica: quase sempre é DNS.

Até mesmo assumir que você recarregou uma configuração, quando na verdade não recarregou, é um erro comum. Seja rigoroso com o seu processo. Verifique em cada nível.

## Reproduza o comportamento

Este é um passo-chave que muitas vezes faz os problemas desaparecerem sozinhos: faça o problema acontecer novamente.

Especificamente, faça isso acontecer novamente _da forma mais minimal possível_. Elimine configurações desnecessárias, etapas de implantação, fatores ambientais etc., até que o problema desapareça.

Uma estratégia comum é eliminar apenas uma coisa por vez e tentar novamente até o problema desaparecer. Então aquilo que você removeu provavelmente é a causa, ou &mdash; e este é um bom momento para duvidar das suposições &mdash; alguma combinação da última coisa removida com a anterior é a causa. Verifique reintroduzindo as primeiras coisas removidas. Vá estreitando.

Outra ideia é eliminar cerca de metade de tudo a cada iteração e, quando o problema desaparecer, eliminar apenas metade dessa metade, e assim por diante. Isso é como uma busca binária e pode ser mais rápido.

Alternativamente, em vez de eliminar, você pode inverter essas estratégias e construir sua configuração ou cenário de baixo para cima, tentando novamente a cada passo, até o problema aparecer.

Muitas vezes, esse processo sozinho já identifica o problema e a solução pode ficar óbvia. Se não, pelo menos você pode anotar os passos mínimos para reproduzir o problema.

## Explore comportamentos

Com os passos conhecidos para reproduzir o problema, você está bem posicionado para diagnosticar a causa. Isso envolve experimentar e, se você tiver prática, ler o código.

Se você não consegue explicar por que o problema está acontecendo, varie o comportamento. Faça uma pequena mudança e tente novamente. Por exemplo, se sua configuração relevante envolve uma expressão regular, altere/simplifique a expressão &mdash; ou remova-a completamente &mdash; e veja se você consegue _alguma coisa_ que produza o comportamento que está procurando. Mesmo que não seja o que você quer, pelo menos você sabe que o problema está na expressão regular ou na configuração.

À medida que explora, observe padrões do que funciona e do que não funciona. Isso deve levar você ao caminho de uma solução.

Se você encontrar uma solução, então pode decidir se isso deveria ser considerado um bug ou não. Às vezes não é óbvio se é um bug; não há problema em abrir um issue com seus experimentos e obter feedback dos mantenedores de qualquer forma.

E se não for um bug, parabéns! Você resolveu um problema e aprendeu pelo menos alguma coisa no processo.

Considere compartilhar sua experiência [no fórum](https://caddy.community) para ajudar outras pessoas que possam encontrar o mesmo problema.
