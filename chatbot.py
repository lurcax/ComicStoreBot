import nltk
from nltk.chat.util import Chat, reflections
from nltk.tokenize import word_tokenize
from fuzzywuzzy import fuzz
from flask import Flask, render_template, request

app = Flask(__name__)

nltk.download('punkt')

pairs = [
    [
        r"oi|olá|hey|hello",
        ["Oi! Bem-vindo à loja virtual de quadrinhos!", "Olá! Como posso ajudar você hoje?", "Hey! Como posso tornar o seu dia mais heróico?"]
    ],
    [
        r"quais quadrinhos vocês oferecem.*|quais são os quadrinhos disponíveis.*",
        ["Nós oferecemos uma ampla variedade de quadrinhos, incluindo super-heróis, mangás e graphic novels. Qual tipo você está procurando?", "Temos uma seleção diversificada de quadrinhos, desde os clássicos até os lançamentos mais recentes."]
    ],
    [
        r"vocês têm quadrinhos de super-heróis.*|quais super-heróis estão disponíveis.*",
        ["Sim, temos uma vasta coleção de quadrinhos de super-heróis! Batman, Superman, Homem-Aranha e muitos outros. Qual é o seu herói favorito?", "Com certeza! Você encontrará uma variedade de quadrinhos dos seus super-heróis favoritos aqui."]
    ],
    [
        r"vocês têm mangá.*|quais títulos de mangá vocês têm.*",
        ["Sim, temos uma seção dedicada a mangás! Naruto, One Piece, Attack on Titan e muito mais. Qual mangá você está interessado?", "Nós amamos mangás também! Temos uma coleção impressionante de títulos populares e clássicos."]
    ],
    [
        r"vocês têm edições raras de quadrinhos.*|quais são as edições de quadrinhos colecionáveis.*",
        ["Definitivamente! Temos edições limitadas e raras para os colecionadores. Se você está procurando algo específico, deixe-me saber.", "Sim, nós valorizamos os colecionadores! Temos uma seção de edições raras que pode te interessar."]
    ],
    [
        r"como faço para fazer um pedido.*|como comprar quadrinhos.*",
        ["Fazer um pedido é fácil! Basta navegar pela nossa loja, escolher os quadrinhos que deseja e adicionar ao carrinho. Depois, siga as instruções de checkout.", "Comprar quadrinhos é simples! Basta adicionar os itens ao seu carrinho e seguir as etapas de pagamento."]
    ],
    [
        r"vocês oferecem frete grátis.*|qual é a política de frete.*",
        ["Nós oferecemos frete grátis em pedidos acima de $50! Caso contrário, as taxas de envio variam de acordo com o destino e o peso do pacote.", "Sim, para pedidos acima de $50, o frete é gratuito! Para pedidos menores, as taxas de envio são calculadas durante o checkout."]
    ],
    [
        r"qual é a política de devolução.*|como posso devolver um quadrinho.*",
        ["Nossa política de devolução permite que você devolva os quadrinhos dentro de 30 dias após a compra, desde que estejam em condições de revenda. Entre em contato conosco para iniciar o processo de devolução.", "Se você precisar devolver um quadrinho, fique tranquilo! Aceitamos devoluções dentro de 30 dias. Entre em contato e teremos prazer em ajudar."]
    ],
    [
        r"vocês têm descontos ou promoções.*|como posso obter cupons de desconto.*",
        ["Sim, frequentemente temos descontos e promoções especiais! Recomendo inscrever-se em nossa newsletter para receber notificações sobre ofertas exclusivas e cupons de desconto.", "Claro! Mantenha-se atualizado sobre nossas promoções incríveis assinando a nossa newsletter. Assim, você não perderá nenhum desconto."]
    ],
    [
        r"vocês têm um programa de fidelidade.*|como funciona o programa de recompensas.*",
        ["Sim, temos um programa de fidelidade emocionante! Cada compra acumula pontos que podem ser usados para descontos futuros. É nossa maneira de agradecer aos nossos clientes fiéis.", "Com certeza! Nosso programa de recompensas permite que você ganhe pontos a cada compra, que podem ser trocados por descontos em compras futuras. É uma forma de retribuir a sua lealdade."]
    ],
    
    [
        r"vocês oferecem entrega expressa?|qual é a opção de entrega mais rápida?",
        ["Sim, oferecemos entrega expressa para quem deseja receber seus quadrinhos rapidamente! Durante o checkout, você poderá selecionar a opção de entrega expressa.", "Com certeza! Se você precisa dos seus quadrinhos o mais rápido possível, opte pela entrega expressa durante o checkout."]
    ],
    [
        r"vocês têm um programa de indicação de amigos?|como posso indicar amigos e ganhar recompensas?",
        ["Sim, temos um programa de indicação! Você pode indicar amigos através de um link exclusivo. Quando eles fizerem uma compra, você receberá recompensas ou descontos como agradecimento.", "Com certeza! Nosso programa de indicação recompensa você por trazer amigos para a nossa loja. Eles ganham e você também!"]
    ],
    [
        r"vocês têm uma loja física?|onde posso encontrar sua loja?",
        ["Atualmente, operamos apenas online e não temos uma loja física. Você pode navegar e comprar quadrinhos diretamente do nosso site.", "Somos uma loja virtual, então todos os nossos produtos estão disponíveis para compra online através do nosso site."]
    ],
    [
        r"vocês têm quadrinhos autografados?|quais quadrinhos têm assinaturas de artistas?",
        ["Sim, temos quadrinhos autografados por artistas! Procure a categoria de quadrinhos autografados no nosso site para ver os títulos disponíveis.", "Com certeza! Nós oferecemos quadrinhos com assinaturas de artistas, o que os torna itens de colecionador únicos."]
    ],
    [
        r"vocês oferecem descontos para compras recorrentes?|como posso obter um desconto em assinaturas mensais?",
        ["Sim, oferecemos descontos para assinaturas mensais de quadrinhos! Ao se inscrever para receber quadrinhos regularmente, você economiza e nunca perde uma edição.", "Definitivamente! Com as nossas assinaturas mensais, você recebe descontos em quadrinhos entregues regularmente, para que você nunca perca uma edição."]
    ],
    [
        r"vocês têm quadrinhos para crianças?|quais são os quadrinhos adequados para crianças?",
        ["Sim, temos quadrinhos para crianças de todas as idades! Nossa seleção inclui quadrinhos apropriados para diferentes faixas etárias, então há algo para todos.", "Com certeza! Temos uma variedade de quadrinhos adequados para crianças, que são perfeitos para iniciar a paixão pelos quadrinhos desde cedo."]
    ],
    [
        r"vocês têm eventos de lançamento?|como posso participar de um evento de lançamento?",
        ["Sim, ocasionalmente realizamos eventos de lançamento! Mantenha-se informado seguindo nossas redes sociais e o nosso site para obter informações sobre os próximos eventos e como participar.", "Definitivamente! Se você quiser participar dos nossos eventos de lançamento emocionantes, basta ficar de olho nas nossas redes sociais e no nosso site para atualizações."]
    ],
    [
        r"vocês oferecem descontos para grupos?|como posso obter um desconto para um grupo de fãs?",
        ["Sim, oferecemos descontos para grupos de fãs! Se você está organizando um grupo interessado em comprar quadrinhos, entre em contato conosco para discutir os descontos disponíveis.", "Claro! Se você está coordenando um grupo de fãs que querem comprar quadrinhos, fale conosco e teremos o prazer de discutir opções de desconto."]
    ],
    [
        r"vocês têm um programa de curadoria?|como posso receber recomendações personalizadas de quadrinhos?",
        ["Sim, temos um programa de curadoria! Se você quiser receber recomendações personalizadas de quadrinhos com base nos seus gostos, entre em contato e nossa equipe terá prazer em ajudar.", "Com certeza! Se você está procurando quadrinhos sob medida para os seus gostos, nossa equipe de curadores está pronta para ajudar."]
    ],
    
    [
        r"vocês têm quadrinhos digitais?|como posso comprar quadrinhos online?",
        ["Sim, oferecemos quadrinhos digitais para os fãs que preferem ler no formato digital! Basta navegar pela nossa coleção digital e comprar os quadrinhos de sua escolha.", "Definitivamente! Temos uma seleção de quadrinhos digitais para quem gosta de ler no formato online. Basta navegar e escolher os títulos que você deseja."]
    ],
    [
        r"vocês têm promoções sazonais?|quais são as ofertas especiais desta temporada?",
        ["Sim, frequentemente temos promoções sazonais que oferecem descontos exclusivos em quadrinhos selecionados! Verifique nosso site para descobrir as ofertas atuais.", "Com certeza! Nossas promoções sazonais oferecem ótimas oportunidades para economizar em quadrinhos durante todo o ano."]
    ],
    [
        r"vocês têm quadrinhos independentes?|quais quadrinhos de artistas independentes estão disponíveis?",
        ["Sim, valorizamos quadrinhos independentes e apoiamos artistas independentes! Temos uma seleção de quadrinhos de artistas talentosos. Dê uma olhada!", "Com certeza! Temos uma seção dedicada a quadrinhos independentes, onde você pode descobrir trabalhos incríveis de artistas independentes."]
    ],
    [
        r"vocês têm edições em capa dura?|quais quadrinhos têm versões em capa dura?",
        ["Sim, temos quadrinhos em edições de capa dura para quem aprecia uma apresentação mais premium! Verifique nossa seleção para encontrar os títulos disponíveis.", "Definitivamente! Se você gosta de quadrinhos em edições de capa dura, temos várias opções elegantes para você escolher."]
    ],
    [
        r"vocês têm acessórios para fãs de quadrinhos?|quais acessórios estão disponíveis?",
        ["Sim, oferecemos uma variedade de acessórios para fãs de quadrinhos! De camisetas a canecas, temos itens exclusivos para mostrar o seu amor pelos quadrinhos.", "Com certeza! Nossa seleção de acessórios inclui camisetas, canecas e muito mais para complementar a sua paixão por quadrinhos."]
    ],
    [
        r"vocês têm eventos de autógrafos?|quando será o próximo evento de autógrafos?",
        ["Sim, realizamos eventos de autógrafos com artistas convidados! Siga nossas redes sociais e fique atento ao nosso site para saber sobre os próximos eventos e autógrafos.", "Definitivamente! Nossos eventos de autógrafos são emocionantes. Mantenha-se informado sobre as datas e convidados seguindo nossas redes sociais e site."]
    ],
    [
        r"vocês têm quadrinhos em línguas estrangeiras?|quais idiomas estão disponíveis?",
        ["Sim, temos quadrinhos em diferentes idiomas estrangeiros! Se você está procurando por quadrinhos em um idioma específico, verifique nossa seleção para ver o que temos disponível.", "Com certeza! Temos quadrinhos em várias línguas estrangeiras para atender às suas preferências de leitura."]
    ],
    [
        r"vocês têm pacotes de colecionador?|quais são os pacotes de quadrinhos disponíveis?",
        ["Sim, oferecemos pacotes de colecionador com diversos quadrinhos em um conjunto! Esses pacotes são perfeitos para os fãs que querem expandir suas coleções de maneira conveniente.", "Definitivamente! Nossos pacotes de colecionador oferecem uma maneira incrível de adquirir vários quadrinhos em um único conjunto."]
    ],
    [
        r"vocês têm eventos de cosplay?|quando será o próximo evento de cosplay?",
        ["Sim, realizamos eventos de cosplay divertidos! Fique de olho em nossas redes sociais e site para informações sobre os próximos eventos de cosplay e como participar.", "Com certeza! Se você é um fã de cosplay, nossos eventos são imperdíveis. Siga-nos para saber sobre os próximos encontros."]
    ],
    [
        r"vocês têm edições de aniversário?|quais quadrinhos têm edições comemorativas de aniversário?",
        ["Sim, temos edições de aniversário para celebrar marcos importantes! Procure por edições comemorativas em nosso site para encontrar quadrinhos especiais.", "Definitivamente! As edições de aniversário são perfeitas para comemorar momentos especiais. Confira nossa seleção para ver as opções disponíveis."]
    ],
    [
        r"vocês têm um programa de envio automático?|como posso receber quadrinhos automaticamente?",
        ["Sim, oferecemos um programa de envio automático para assinaturas mensais! Inscreva-se e escolha os quadrinhos que deseja receber regularmente, e cuidaremos do resto.", "Com certeza! Nosso programa de envio automático garante que você nunca perca uma edição. Basta se inscrever e escolher seus quadrinhos favoritos."]
    ],
    [
        r"vocês têm quadrinhos de ficção científica?|quais são os quadrinhos de ficção científica disponíveis?",
        ["Sim, temos uma coleção de quadrinhos de ficção científica! Se você gosta de histórias de viagens no tempo, alienígenas e tecnologia futurista, você vai adorar nossa seleção.", "Definitivamente! Os fãs de ficção científica encontrarão uma variedade de quadrinhos emocionantes em nossa coleção."]
    ],
    [
        r"vocês têm uma política de privacidade?|como vocês protegem os meus dados?",
        ["Sim, temos uma política de privacidade rigorosa para proteger seus dados! Valorizamos a sua privacidade e tomamos medidas para garantir a segurança das suas informações pessoais.", "Com certeza! A sua privacidade é importante para nós. Nossa política de privacidade detalha como protegemos e usamos seus dados."]
    ],
    [
        r"vocês têm quadrinhos de terror?|quais são os quadrinhos de terror disponíveis?",
        ["Sim, temos uma coleção de quadrinhos de terror para os fãs de sustos e arrepios! Explore nossa seleção para descobrir quadrinhos assustadores e emocionantes.", "Definitivamente! Nossa coleção de quadrinhos de terror oferece histórias emocionantes para os amantes do gênero."]
    ],
    [
        r"vocês têm quadrinhos de aventura?|quais são os quadrinhos de aventura disponíveis?",
        ["Sim, temos uma coleção de quadrinhos de aventura repletos de ação e emoção! Se você gosta de histórias cheias de reviravoltas e desafios, confira nossa seleção.", "Com certeza! Nossos quadrinhos de aventura são perfeitos para quem procura emoção e adrenalina nas páginas."]
    ],
    [
        r"vocês têm um blog ou conteúdo informativo?|onde posso encontrar artigos sobre quadrinhos?",
        ["Sim, temos um blog repleto de artigos e conteúdo informativo sobre quadrinhos! Visite nosso site e confira nossa seção de blog para se manter atualizado.", "Definitivamente! Se você está procurando por artigos interessantes e informativos sobre quadrinhos, nosso blog é o lugar certo."]
    ],
    [
        r"vocês têm quadrinhos de fantasia?|quais são os quadrinhos de fantasia disponíveis?",
        ["Sim, temos uma coleção de quadrinhos de fantasia cheios de magia e mundos imaginários! Explore nossa seleção para descobrir histórias emocionantes.", "Com certeza! Nossos quadrinhos de fantasia transportarão você para mundos mágicos e emocionantes."]
    ],
    [
        r"vocês oferecem opções de pagamento seguras?|como posso ter certeza da segurança do meu pagamento?",
        ["Sim, oferecemos opções de pagamento seguras para garantir a sua tranquilidade! Utilizamos métodos de pagamento seguros para proteger suas informações financeiras.", "Definitivamente! A segurança do seu pagamento é importante para nós. Utilizamos métodos de pagamento confiáveis para garantir a proteção das suas informações."]
    ],
    [
        r"vocês têm quadrinhos de romance?|quais são os quadrinhos de romance disponíveis?",
        ["Sim, temos uma coleção de quadrinhos de romance para os fãs de histórias apaixonantes! Explore nossa seleção para descobrir quadrinhos cheios de corações e emoções.", "Com certeza! Nossos quadrinhos de romance oferecem histórias emocionais e cativantes para os amantes do gênero."]
    ],
    [
        r"vocês têm quadrinhos históricos?|quais são os quadrinhos históricos disponíveis?",
        ["Sim, temos uma coleção de quadrinhos históricos que exploram diferentes períodos do passado! Se você gosta de histórias ambientadas em épocas antigas, você vai adorar nossa seleção.", "Definitivamente! Nossos quadrinhos históricos oferecem uma viagem no tempo para diferentes momentos da história."]
    ],
    [
        r"vocês têm um programa de afiliados?|como posso me tornar um afiliado e ganhar comissões?",
        ["Sim, temos um programa de afiliados! Se você deseja ganhar comissões promovendo nossa loja, entre em contato conosco para obter mais informações sobre como se tornar um afiliado.", "Com certeza! Nosso programa de afiliados oferece a oportunidade de ganhar comissões através da promoção da nossa loja. Entre em contato para saber mais."]
    ],
    [
        r"vocês têm quadrinhos de comédia?|quais são os quadrinhos de comédia disponíveis?",
        ["Sim, temos uma coleção de quadrinhos de comédia para os fãs de risadas e bom humor! Explore nossa seleção para descobrir quadrinhos divertidos e engraçados.", "Definitivamente! Nossos quadrinhos de comédia são perfeitos para quem procura histórias leves e divertidas."]
    ],
    [
        r"vocês têm uma seção de pré-venda?|como posso encomendar quadrinhos em pré-venda?",
        ["Sim, temos uma seção de pré-venda para os títulos futuros mais empolgantes! Para encomendar quadrinhos em pré-venda, basta visitar a seção correspondente no nosso site e seguir as instruções.", "Com certeza! Nossa seção de pré-venda é ideal para garantir os quadrinhos mais esperados antes do lançamento oficial."]
    ],
    [
        r"vocês têm um programa de doações ou caridade?|como vocês estão envolvidos em causas sociais?",
        ["Sim, estamos comprometidos com causas sociais e apoiamos iniciativas de caridade! Fique atento ao nosso site e redes sociais para informações sobre nossos programas de doações e envolvimento em causas.", "Definitivamente! A responsabilidade social é importante para nós. Mantenha-se informado sobre nossas iniciativas de caridade e envolvimento seguindo nossas redes sociais e site."]
    ],
    [
        r"vocês têm quadrinhos educativos?|quais são os quadrinhos educativos disponíveis?",
        ["Sim, temos uma coleção de quadrinhos educativos que combinam entretenimento e aprendizado! Se você gosta de aprender enquanto lê, explore nossa seleção de quadrinhos educativos.", "Com certeza! Nossos quadrinhos educativos oferecem uma maneira divertida e envolvente de adquirir conhecimento."]
    ],
    [
        r"vocês têm opções de presente?|como posso comprar quadrinhos como presente?",
        ["Sim, oferecemos opções de presente para que você possa surpreender os amantes de quadrinhos! Ao fazer um pedido, você pode optar por enviá-lo como presente e incluir uma mensagem personalizada.", "Definitivamente! Nossas opções de presente permitem que você compartilhe a paixão pelos quadrinhos com amigos e familiares. Basta selecionar a opção de presente durante o checkout."]
    ],
    [
        r"vocês têm quadrinhos de horror?|quais são os quadrinhos de terror disponíveis?",
        ["Sim, temos uma coleção de quadrinhos de horror para os fãs de sustos e emoções! Explore nossa seleção para descobrir quadrinhos assustadores e cheios de suspense.", "Definitivamente! Nossa coleção de quadrinhos de horror oferece uma variedade de histórias arrepiantes para os amantes do gênero."]
    ],
    [
        r"vocês têm quadrinhos LGBTQ+?|quais são os quadrinhos com representação LGBTQ+ disponíveis?",
        ["Sim, temos uma coleção de quadrinhos com representação LGBTQ+! Valorizamos a diversidade e oferecemos uma variedade de quadrinhos que abordam temas relacionados à comunidade LGBTQ+.", "Com certeza! Nossa coleção inclui quadrinhos com histórias emocionantes e relevantes para a comunidade LGBTQ+."]
    ],
    [
        r"vocês têm quadrinhos clássicos?|quais são os quadrinhos clássicos disponíveis?",
        ["Sim, temos uma seleção de quadrinhos clássicos que resistiram ao teste do tempo! Se você está interessado em obras atemporais, confira nossa coleção de quadrinhos clássicos.", "Definitivamente! Nossos quadrinhos clássicos são perfeitos para quem quer explorar os títulos que moldaram a história dos quadrinhos."]
    ],
    [
        r"vocês oferecem opções de embalagem especial?|como posso solicitar uma embalagem de presente?",
        ["Sim, oferecemos opções de embalagem especial para presentes! Durante o processo de checkout, você pode optar por adicionar uma embalagem de presente e incluir uma mensagem personalizada para o destinatário.", "Com certeza! Se você quiser que a sua compra seja embrulhada como um presente, basta escolher a opção de embalagem especial durante o checkout."]
    ],
    [
        r"vocês têm quadrinhos de mistério?|quais são os quadrinhos de mistério disponíveis?",
        ["Sim, temos uma coleção de quadrinhos de mistério cheios de enigmas e intrigas! Se você gosta de desvendar segredos, confira nossa seleção de quadrinhos de mistério.", "Definitivamente! Nossos quadrinhos de mistério oferecem histórias envolventes e cheias de suspense para os amantes do gênero."]
    ],
    [
        r"vocês têm uma seção de quadrinhos nacionais?|quais são os quadrinhos nacionais disponíveis?",
        ["Sim, temos uma seleção de quadrinhos nacionais! Valorizamos a produção nacional e oferecemos uma variedade de quadrinhos de artistas brasileiros talentosos.", "Com certeza! Nossa coleção inclui quadrinhos de artistas nacionais que enriquecem o cenário dos quadrinhos brasileiros."]
    ],
    [
        r"vocês têm quadrinhos de guerra?|quais são os quadrinhos de guerra disponíveis?",
        ["Sim, temos uma coleção de quadrinhos de guerra que exploram diferentes aspectos dos conflitos! Se você está interessado em histórias ambientadas em tempos de guerra, confira nossa seleção.", "Definitivamente! Nossos quadrinhos de guerra oferecem uma perspectiva única sobre os eventos históricos e os impactos dos conflitos."]
    ],
    [
        r"vocês têm quadrinhos de superpoderes?|quais são os quadrinhos de superpoderes disponíveis?",
        ["Sim, temos uma coleção de quadrinhos de superpoderes para os fãs de ação sobrenatural! Explore nossa seleção para descobrir quadrinhos cheios de heróis e vilões com habilidades extraordinárias.", "Com certeza! Nossos quadrinhos de superpoderes oferecem emocionantes batalhas entre personagens com habilidades especiais."]
    ],
    [
        r"vocês têm uma seção de quadrinhos europeus?|quais são os quadrinhos europeus disponíveis?",
        ["Sim, temos uma seleção de quadrinhos europeus! Se você está interessado em explorar quadrinhos de diferentes culturas, nossa coleção inclui títulos europeus populares.", "Definitivamente! Nossa coleção de quadrinhos inclui trabalhos de autores europeus que oferecem perspectivas únicas e narrativas cativantes."]
    ],
    [
        r"vocês têm quadrinhos de drama?|quais são os quadrinhos de drama disponíveis?",
        ["Sim, temos uma coleção de quadrinhos de drama emocionantes! Se você gosta de histórias que exploram emoções e relacionamentos complexos, confira nossa seleção de quadrinhos de drama.", "Com certeza! Nossos quadrinhos de drama oferecem narrativas envolventes que exploram os aspectos emocionais da vida."]
    ]
    # Mais pares de perguntas e respostas podem ser adicionados aqui
]

def fuzzy_match(user_input, patterns):
    best_match = None
    highest_similarity = 0

    for pattern, _ in patterns:
        similarity = fuzz.partial_ratio(user_input, pattern)
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = pattern

    return best_match

@app.route("/", methods=["GET", "POST"])
def index():
    chatbot = Chat(pairs, reflections)
    if request.method == "POST":
        user_input = request.form["user_input"]
        matched_pattern = fuzzy_match(user_input, pairs)
        if matched_pattern:
            response = chatbot.respond(matched_pattern)
        else:
            response = "Desculpe, não entendi. Pode reformular a pergunta?"
        return render_template("index.html", user_input=user_input, response=response)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)