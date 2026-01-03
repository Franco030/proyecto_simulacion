from model import engine, Base, SessionLocal
from model import Question, Option, User
from sqlalchemy.exc import IntegrityError
import bcrypt

# -------------------------------------------------------------------
# DATOS DE LAS PREGUNTAS
# Extraídos del archivo "Test de Inglés WORD con Respuestas.docx"
# -------------------------------------------------------------------

questions_data = {
    "Beginner": [
        {
            "text": "Hello, Jack. How are you?\n_____ Sophie! I’m great, thanks.",
            "options": ["Hi", "Bye", "Goodbye", "Of course"],
            "correct_answer": "Hi"
        },
        {
            "text": "Hey, do you know that girl?\nSure! ____ is the new student, Martha.",
            "options": ["He", "They", "She", "We"],
            "correct_answer": "She"
        },
        {
            "text": "Can you see those two men over there?\nThey ____ my brothers, Carl and Craig.",
            "options": ["is", "am", "be", "are"],
            "correct_answer": "are"
        },
        {
            "text": "How old is she?\nShe____ 28 years old.",
            "options": ["has", "is", "are", "have"],
            "correct_answer": "is"
        },
        {
            "text": "Sophie really likes this movie, I think it’s _____ favorite movie because she told me she loves it!",
            "options": ["my", "her", "his", "their"],
            "correct_answer": "her"
        },
        {
            "text": "Hey, where ___ Charlie ___?\nHe is from France.",
            "options": ["are / to", "am / from", "is / for", "is/ from"],
            "correct_answer": "is/ from"
        },
        {
            "text": "I need to buy ___ umbrella, ___ bag, and ____ wallet.",
            "options": ["a / an / a", "an / a / a", "an / an / a", "a / a / an"],
            "correct_answer": "an / a / a"
        },
        {
            "text": "Hey! Laurie, can you see ______ two cars in the distance?",
            "options": ["these", "that", "this", "those"],
            "correct_answer": "those"
        },
        {
            "text": "There are more than ten _____ parked outside.",
            "options": ["bus", "buses", "buzes", "buss"],
            "correct_answer": "buses"
        },
        {
            "text": "Can you describe your house, please?\nYes, It’s really big. __________ a big living room. Also, __________ four bathrooms and four bedrooms.",
            "options": ["there are / there is", "there is / there is", "there is / there are", "there are / there are"],
            "correct_answer": "there is / there are"
        },
        {
            "text": "What animal is this one?",
            "options": ["frog", "tiger", "elephant", "dog"],
            "correct_answer": "tiger", 
            "image_file": "animal_t.jpg"
        },
        {
            "text": "What animal is this one?",
            "options": ["cat", "bear", "frog", "snake"],
            "correct_answer": "frog",
            "image_file": "animal_f.jpg"
        }
    ],
    "Elementary": [
        {
            "text": "Excuse me, ______ can you find a good mall in this city?",
            "options": ["why", "when", "where", "who"],
            "correct_answer": "where"
        },
        {
            "text": "What do you usually do on Monday morning, Susana?\nOh! well… I usually ______ to work and spend the day in the office.",
            "options": ["Goes", "Went", "Going", "Go"],
            "correct_answer": "Go"
        },
        {
            "text": "______ your sister like Pizza?\nYes, she loves it!",
            "options": ["Do", "Does", "Did", "Can"],
            "correct_answer": "Does"
        },
        {
            "text": "My mother really _______ to buy a new car.",
            "options": ["wants", "want", "is wanting", "wanting"],
            "correct_answer": "wants"
        },
        {
            "text": "I usually travel by plane but today I ___________ by bus!",
            "options": ["are travel", "am travel", "am travelling", "are travelling"],
            "correct_answer": "am travelling"
        },
        {
            "text": "What a beautiful car!\nYes, it’s _________. Her father gave it to her on her birthday.",
            "options": ["Lisas’ car", "Lisa her car", "Lisa’s car", "the car of Lisa"],
            "correct_answer": "Lisa’s car"
        },
        {
            "text": "There are a lot of ______ and _______ in this office but no one cares about the infestation of _______ they have.",
            "options": ["mans / womans / mouses", "men / Women / mouses", "men / Womens / mice", "men / women / mice"],
            "correct_answer": "men / women / mice"
        },
        {
            "text": "I am perfect! I never _______ mistakes!",
            "options": ["do", "make", "commit", "take"],
            "correct_answer": "make"
        },
        {
            "text": "This restaurant is amazing! ____ food is good and ____ service is excellent. There is ____ beautiful painting, too.",
            "options": ["An / a / the", "The / the / the", "The / a / a", "The / the / a"],
            "correct_answer": "The / the / a"
        },
        {
            "text": "Take a look at this picture of my new girlfriend. She ____ green eyes and blond hair. Also, she ____ very tall and thin.",
            "options": ["have / is", "is / Has", "has / is", "has / has"],
            "correct_answer": "has / is"
        },
        {
            "text": "Let’s go to the beach on Saturday!\nOh, I _____ swim sorry. But we could go to the French club.\nI _____ speak French George, you know that.",
            "options": ["can / can", "don’t know / don’t know", "can’t / can’t", "no / Don’t"],
            "correct_answer": "can’t / can’t"
        },
        {
            "text": "Where are you on Monday morning?\nI usually spend my mornings ____ the office.",
            "options": ["on", "in", "at", "to"],
            "correct_answer": "in" # (Basado en la clave de respuestas 22. b)
        },
        {
            "text": "Whose notebook is this?\nIt’s _______.",
            "options": ["mine", "my", "her", "their"],
            "correct_answer": "mine"
        },
        {
            "text": "What are some differences between a car and a motorcycle?\nI suppose cars are _______ and _______, too!",
            "options": ["more fast / more expensive", "faster / expensiver", "more fast / expensiver", "faster / more expensive"],
            "correct_answer": "faster / more expensive"
        },
        {
            "text": "I was thinking about our next anniversary.\nMe too! I would _________ it in Asia this year.",
            "options": ["like celebrate", "like to celebrating", "like to celebrate", "to like celebrate"],
            "correct_answer": "like to celebrate"
        }
    ],
    "Pre-intermediate": [
        {
            "text": "Hey Mark, where ____ you ____ last night?\nI went to the supermarket, why?",
            "options": ["did / go", "did / went", "do / went", "do / go"],
            "correct_answer": "did / go"
        },
        {
            "text": "I _____ to her yesterday but I didn’t _____ to you! I swear!",
            "options": ["talk / lied", "talked / lied", "talked / lie", "talk / lie"],
            "correct_answer": "talked / lie"
        },
        {
            "text": "How ______ sugar do you like in your coffee?\nI like my coffee with _____ sugar, not much.",
            "options": ["many / any", "much / some", "many / some", "much / any"],
            "correct_answer": "much / some"
        },
        {
            "text": "I hate my legs! they are ____ fat. My hair is _____ pretty, though.",
            "options": ["too / Too", "really / too", "too / really"], # Opción 4 estaba vacía
            "correct_answer": "too / really"
        },
        {
            "text": "My sister has sleeping problems, can you give me some advice for her?\nShe _____ avoid using her cell phone at night and she _______ drink coffee either.",
            "options": ["needs / doesn’t have to", "should / shouldn’t", "can / could", "must / might"],
            "correct_answer": "should / shouldn’t"
        },
        {
            "text": "What is all this mess? What did you do, Joe?\n___ to your room right now! You’re grounded!",
            "options": ["Went", "Going", "Go", "Gone"],
            "correct_answer": "Go"
        },
        {
            "text": "I ____________ on the phone when my friend Carl knocked on the door.",
            "options": ["am talking", "were talking", "was talking", "is talking"],
            "correct_answer": "was talking"
        },
        {
            "text": "This is the _________ car in the world but I’m afraid it’s not ________.",
            "options": ["most expensive / faster", "most expensive / the fastest", "most expensive / the faster", "expensivest / the fastest"],
            "correct_answer": "most expensive / the fastest"
        },
        {
            "text": "She __________ stay in that hotel on her trip. She’s already booked a room there for a week.",
            "options": ["is going to", "will", "might", "is not going to"],
            "correct_answer": "is going to"
        },
        {
            "text": "Sorry, I can’t talk right now. I_________ call you back later.",
            "options": ["am going to", "will", "will to", "definitely"],
            "correct_answer": "will"
        },
        {
            "text": "_____ you ever _____ Japanese food?\nYes, of course! My grandmother is Japanese.",
            "options": ["Had / eating", "Are / eating", "Have / ate", "Have / eaten"],
            "correct_answer": "Have / eaten"
        },
        {
            "text": "I ___________ driven a car! I hope I will get to drive one next year!",
            "options": ["yet haven’t", "still haven’t", "yet have", "still have"],
            "correct_answer": "still haven’t"
        },
        {
            "text": "Look at that woman on the stage! She is singing my favorite song!\nYes, she sings ________.",
            "options": ["beautiful", "beautifully", "good", "perfect"],
            "correct_answer": "beautifully"
        },
        {
            "text": "Excuse me, do you know ___________ ?",
            "options": ["where is the bus station", "where can I find the bus station", "where the bus station is", "where can be found the bus station"],
            "correct_answer": "where the bus station is"
        },
        {
            "text": "There are a lot of things to do in this house!\nMark, you ____ the laundry and… Mary, you _____ breakfast while I ____ the ironing.",
            "options": ["make / make / do", "do / do / make", "do / do / do", "do / make / do"],
            "correct_answer": "do / make / do"
        }
    ],
    "Intermediate": [
        {
            "text": "________ are going to beat ______ in the upcoming tournament, I’m sure of that!",
            "options": ["You and me / they", "You and I / them", "You and me / them", "You and I / they"],
            "correct_answer": "You and I / them"
        },
        {
            "text": "Sarah spends too much time in front of the mirror!\nYes, she really loves _______ a bit too much.",
            "options": ["she", "herself", "myself", "her"],
            "correct_answer": "herself"
        },
        {
            "text": "Marie and Joseph are always arguing and insulting _______.",
            "options": ["them", "themselves", "herself", "each other"],
            "correct_answer": "each other"
        },
        {
            "text": "Both of them ____ very competitive!\nYes, you are right. Neither of them ______ to lose!",
            "options": ["are / wants", "are / want", "is / wants", "is / want"],
            "correct_answer": "are / wants"
        },
        {
            "text": "When I was a kid, I _______ walk 10km to go to school everyday.",
            "options": ["was used to", "used to", "will", "went to"],
            "correct_answer": "used to"
        },
        {
            "text": "She really likes playing volleyball, _________?",
            "options": ["doesn’t she?", "does she?", "is she?", "isn’t she?"],
            "correct_answer": "doesn’t she?"
        },
        {
            "text": "If you ______ your room, you ________ to the party tonight.",
            "options": ["cleaned / go", "clean / would go", "cleaned / would go", "clean / will go"],
            "correct_answer": "clean / will go"
        },
        {
            "text": "I wanted to ____ together with my friends in the club tonight!",
            "options": ["go", "be", "get", "have"],
            "correct_answer": "get"
        },
        {
            "text": "The environment ___________ get better if we continue to pollute the air like we do!",
            "options": ["will definitely", "won’t definitely", "definitely will", "definitely won’t"],
            "correct_answer": "definitely won’t"
        },
        {
            "text": "I have _________ this book for weeks and I think I will never finish it! It’s too long!",
            "options": ["read", "been read", "been reading", "reading"],
            "correct_answer": "been reading"
        },
        {
            "text": "My parents usually make me ________ my homework and they never let me_____ outside with the other kids!",
            "options": ["do / play", "to do / to play", "to do / play", "do / to play"],
            "correct_answer": "do / play"
        },
        {
            "text": "When I arrived at the restaurant Mark _________.\nYes, he ____________ for me for more than one hour.",
            "options": ["has left / was waiting", "had left / had been waiting", "left / was waiting", "had been leaving / waited"],
            "correct_answer": "had left / had been waiting"
        },
        {
            "text": "Joseph _______ me that he was leaving the country today.\nYes, he _______ the same thing in the meeting the other day.",
            "options": ["said / told", "said / said", "told / told", "told / said"],
            "correct_answer": "told / said"
        },
        {
            "text": "Did you hear what the boss said yesterday?\nHe said that ________________",
            "options": ["he was going to promote Mary, the secretary.", "he is going to promote Mary, the secretary.", "he will promote Mary, the secretary.", "he went to promote Mary, the secretary."],
            "correct_answer": "he was going to promote Mary, the secretary."
        },
        {
            "text": "Million of books__________ everyday.",
            "options": ["will print", "are print", "printed", "are printed"],
            "correct_answer": "are printed"
        },
        {
            "text": "My son, ______ is a lawyer, works in that big building over there!",
            "options": ["which", "who", "that", "whom"],
            "correct_answer": "who"
        },
        {
            "text": "If I ______ a lot of money, I _________ buy a big house in the hills.",
            "options": ["have / would", "had / will", "had / would", "would / will"],
            "correct_answer": "had / would"
        },
        {
            "text": "Where _____ you go if you _____ fly?\nTo the North Pole, definitely!",
            "options": ["would / could", "will / can", "can / will", "could / would"],
            "correct_answer": "would / could"
        },
        {
            "text": "I hate living in this small town! If only ______ somewhere else!",
            "options": ["I can live", "I could live", "I could lived", "could I live"],
            "correct_answer": "I could live"
        },
        {
            "text": "I wish ________ in a big city!",
            "options": ["I lived", "I am living", "I can live", "I would live"],
            "correct_answer": "I lived"
        },
        {
            "text": "What climate does the image show?",
            "options": ["rainy", "sunny", "foggy", "snowy"],
            "correct_answer": "rainy",
            "image_file": "clima_r.jpg"
        },
        {
            "text": "What climate does the image show?",
            "options": ["windy", "sunny", "foggy", "snowy"],
            "correct_answer": "foggy",
            "image_file": "clima_f.jpg"
        }
    ],
    "Upper-intermediate": [
        {
            "text": "I hate having to walk to school!\nI don’t hate it. I ______ used to _____ it every day.",
            "options": ["will / do", "am / doing", "am / do", "— / doing"],
            "correct_answer": "am / doing"
        },
        {
            "text": "We had an incredible time at the party last night!\nOhh, if only I ________ you guys! now I regret it .",
            "options": ["joined", "did join", "had joined", "have joined"],
            "correct_answer": "had joined"
        },
        {
            "text": "You haven’t found your keys____, have you?\nNo, I ______ haven’t.",
            "options": ["yet / already", "still / yet", "yet / yet", "yet / still"],
            "correct_answer": "yet / still"
        },
        {
            "text": "Why hasn’t the teacher arrived?\nI don’t know. He _________ in traffic.",
            "options": ["was caught", "might have caught", "might have been caught", "was definitely caught"],
            "correct_answer": "might have been caught"
        },
        {
            "text": "Why do people care more about social media sites than the real life?\nThat’s not true, it’s mostly teenagers. ________ people or so, you know.",
            "options": ["15-years-old", "15-year-old", "15 year old", "15 years old"],
            "correct_answer": "15-year-old"
        },
        {
            "text": "Martial arts were created in _______ to fight attackers back!",
            "options": ["relation", "consequence", "intention", "order"],
            "correct_answer": "order"
        },
        {
            "text": "My mother feels really bad!\nI suggest ________________ to the doctor.",
            "options": ["her to go", "that she go", "that she goes", "her go"],
            "correct_answer": "that she go"
        },
        {
            "text": "If I _______________ to that party, I __________ a great time! Too bad I didn’t go.",
            "options": ["had gone / would have had", "had gone / would have", "went / would have had", "go / would"],
            "correct_answer": "had gone / would have had"
        },
        {
            "text": "When you wake up tomorrow morning, I ________ driving my car 100 km away from here.",
            "options": ["be", "will be", "will", "would be"],
            "correct_answer": "will be"
        },
        {
            "text": "We need that report by Monday morning urgently!\nI will ________ the report by tomorrow morning for sure.",
            "options": ["have written", "write", "have had written", "writing"],
            "correct_answer": "have written"
        },
        {
            "text": "What item does the image show?",
            "options": ["cup", "pen", "carpet", "folder"],
            "correct_answer": "folder",
            "image_file": "item_f.jpg"
        }
    ],
    "Advanced": [
        {
            "text": "You are _______ a good person. You are always helping others and that’s ___ amazing!",
            "options": ["so / so", "such / so", "such / such", "so / such"],
            "correct_answer": "such / so"
        },
        {
            "text": "I am selling a ______________ table from the 18th century, are you interested?",
            "options": ["beautiful, wooden, round", "round, wooden, beautiful", "beautiful, round, wooden", "wooden, beautiful, round"],
            "correct_answer": "beautiful, round, wooden"
        },
        {
            "text": "This product is amazing! Not only________ clean and dry with it, but you can also use it as a tablecloth!",
            "options": ["you can", "can you", "can", "you"],
            "correct_answer": "can you"
        },
        {
            "text": "Nobody knew it at that time but he ______ one of the most successful pop artist ten years later!",
            "options": ["will become", "would become", "became", "would have become"],
            "correct_answer": "would become"
        },
        {
            "text": "I have a big collection of cars, ___________ are Ferrari!",
            "options": ["from three", "three of which", "three of whom", "from which three"],
            "correct_answer": "three of which"
        }
    ]
}


def create_tables():
    """Crea todas las tablas en la base de datos."""
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas exitosamente.")

def populate_questions():
    """Puebla la base de datos con las preguntas y opciones."""
    
    # Creamos una sesión
    db = SessionLocal()
    
    try:
        # Verificamos si la base de datos ya está poblada
        question_count = db.query(Question).count()
        if question_count > 0:
            print(f"La base de datos ya contiene {question_count} preguntas. No se agregarán más.")
            return

        print("Poblando la base de datos con preguntas y opciones...")
        
        new_questions = []
        
        # Iteramos sobre cada nivel (Beginner, Elementary, etc.)
        for level, questions in questions_data.items():
            # Iteramos sobre cada pregunta dentro de ese nivel
            for q_data in questions:
                
                # Creamos las opciones para esta pregunta
                options_list = []
                for opt_text in q_data["options"]:
                    if not opt_text: continue # Ignoramos opciones vacías
                    
                    is_correct = (opt_text == q_data["correct_answer"])
                    options_list.append(Option(text=opt_text, is_correct=is_correct))
                
                # Creamos la pregunta y le asignamos sus opciones
                new_q = Question(
                    text=q_data["text"],
                    level=level,
                    options=options_list,
                    image_path=q_data.get("image_file")
                )
                new_questions.append(new_q)
        
        # Agregamos todas las nuevas preguntas (y sus opciones en cascada) a la sesión
        db.add_all(new_questions)
        
        # Confirmamos la transacción
        db.commit()
        print(f"¡Éxito! Se agregaron {len(new_questions)} preguntas a la base de datos.")

    except Exception as e:
        print(f"Error al poblar la base de datos: {e}")
        db.rollback() # Revertimos la transacción en caso de error
    finally:
        db.close() # Siempre cerramos la sesión

def create_admin_user():
    """
    Crea el usuario administrador 'admin' con contraseña 'admin123'
    si no existe ya.
    """
    print("Verificando usuario administrador...")
    db = SessionLocal()
    try:
        # Verificamos si el usuario 'admin' ya existe
        admin_user = db.query(User).filter_by(username='admin').first()
        if admin_user:
            print("El usuario 'admin' ya existe.")
            return

        # Si no existe, lo creamos
        print("Creando usuario 'admin'...")
        # Hasheamos la contraseña 'admin123'
        password = 'admin123'
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        new_admin = User(username='admin', password_hash=hashed_pw)
        db.add(new_admin)
        db.commit()
        print("Usuario 'admin' creado exitosamente.")
        
    except IntegrityError:
        db.rollback()
        print("Error de integridad. El usuario 'admin' probablemente ya existe.")
    except Exception as e:
        db.rollback()
        print(f"Error al crear el usuario admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    populate_questions()
    create_admin_user()