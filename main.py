import streamlit as st
import pyttsx3
import speech_recognition as sr
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
from streamlit_option_menu import option_menu
from streamlit_chat import message
from utils import *
from googletrans import Translator
import os
import google.generativeai as genai
from PIL import Image
import json
from dotenv import load_dotenv


# Voice assistant setup
def speak(text, language='en'):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('voice', f'com.apple.speech.synthesis.voice.{language}')
    engine.say(text)
    engine.runAndWait()


def listen(language='en'):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language=language)
        print(f"User said: {query}\n")
    except Exception as e:
        print("Say that again please...")
        query = None
    return query


# Main app setup
# Main app setup
def main():
    st.set_page_config(page_title="PetCareMate")

    # Load and display the logo image
    #logo_image = Image.open(r" https://github.com/MANOJ9902/aventus/blob/main/imageedit_1_5862279130.png ")
    #st.sidebar.image(logo_image, use_column_width=True)

    st.header('Welcome to :violet[PetCareMate]')
    st.write(
        ":red[Keep in mind, I'm not a doctor. While I can help with initial stages of pet health issues, for optimal results, it's always best to consult a professional veterinarian!]")




    class AHome:
        @staticmethod
        def app():

            target_language = st.selectbox("Select Translation Language",
                                           ['en', 'kn', 'te', 'hi', 'bn''mr', 'ta', 'ur', 'gu', 'ml'])  # Add more languages as needed
            try:
                if 'responses' not in st.session_state:
                    st.session_state['responses'] = ["Hello!, How can I assist you?"]

                if 'requests' not in st.session_state:
                    st.session_state['requests'] = []

                with open('config.json') as config_file:
                    config = json.load(config_file)
                    api_key = config.get('openai_api_key', None)

                if api_key is None:
                    st.error("API key is missing. Please provide a valid API key in the config.json file.")
                    st.stop()
                else:
                    llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=api_key)

                    if 'buffer_memory' not in st.session_state:
                        st.session_state.buffer_memory = ConversationBufferWindowMemory(k=5, return_messages=True)
            except ValueError:
                st.error("Incorrect API key provided. Please check and update the API key in the config.json file.")
                st.stop()
            except Exception as e:
                st.error("An error occurred during initialization: " + str(e))
                llm = None
                st.session_state.buffer_memory = None

            # Rest of your Streamlit app code...

            system_msg_template = SystemMessagePromptTemplate.from_template(
                template="""Please provide helpful information related to pet care and well-being based on your knowledge base. If the question is apart from pet care, please respond with 'I'm sorry, but I'm not equipped to answer that question at the moment. My expertise lies within certain domains, and this topic falls outside of those areas. However, I'm here to assist you with any inquiries within my capabilities. Is there anything else I can help you with?'
    '"""
            )

            human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")

            prompt_template = ChatPromptTemplate.from_messages(
                [system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])

            conversation = ConversationChain(memory=st.session_state.buffer_memory, prompt=prompt_template, llm=llm,
                                             verbose=True)

            # Container for chat history
            response_container = st.container()
            # Container for text box
            textcontainer = st.container()

            with textcontainer:
                query = st.text_input("Query: ", key="input")
                # Voice assistant integration
                if st.button("🎙️ Speak"):
                    user_query = listen(language='kn')  # Default language is English
                    if user_query:
                        st.text_area("User Query:", user_query)
                        # Process the user query and generate a response
                        response = conversation.predict(input=user_query)
                        st.text_area("Assistant Response:", response)
                        speak(response, language='kn')  # Output in English
                    else:
                        st.text_area("User Query:", "No query detected.")

                # Within the block where you handle user queries and generate responses
                if query:
                    with st.spinner("typing..."):
                        try:
                            conversation_string = get_conversation_string()
                            refined_query = query_refiner(conversation_string, query)
                            st.subheader("Refined Query:")
                            st.write(refined_query)
                            context = find_match(query)

                            if "pet" in context.lower() or "dog" in context.lower() or "cat" in context.lower() or "health" in context.lower() or "care" in context.lower() or "Training" in context.lower() or "nutrition" in context.lower():
                                response = conversation.predict(input=f"Context:\n {context} \n\n Query:\n{query}")

                                def translate_text(text, target_language):
                                    translator = Translator()
                                    translated_text = translator.translate(text, dest=target_language).text
                                    return translated_text

                                try:
                                    response_translated = translate_text(response, target_language)
                                    st.session_state.requests.append(query)
                                    st.session_state.responses.append(response_translated)
                                except Exception as e:
                                    st.error("An error occurred during translation: " + str(e))
                            else:
                                st.warning(
                                    "I'm sorry, but I'm not equipped to answer that question                                    at the moment. My expertise lies within certain domains, and this topic falls outside of those areas. However, I'm here to assist you with any inquiries within my capabilities. Is there anything else I can help you with?")

                        except Exception as e:
                            st.error("An error occurred during conversation: " + str(e))

            with response_container:
                if st.session_state['responses']:
                    for i in range(len(st.session_state['responses'])):
                        try:
                            message(st.session_state['responses'][i], key=str(i))
                            if i < len(st.session_state['requests']):
                                message(st.session_state["requests"][i], is_user=True, key=str(i) + '_user')
                        except Exception as e:
                            st.error("An error occurred while displaying messages: " + str(e))

    class AboutUs:
        @staticmethod
        def app():
            html_content = """
                <style>
                    .header {
                        color: #4CAF50;
                    }
                    .subheader {
                        color: #008CBA;
                    }
                    .highlight {
                        color: #FF9800;
                        font-weight: bold;
                    }
                    .feature-row {
                        display: flex;
                        flex-wrap: wrap;
                        justify-content: space-between;
                        margin-bottom: 20px;
                    }
                    .feature {
                        flex: 0 0 48%; /* Adjust this to control the width of each feature box */
                        margin-bottom: 20px;
                    }
                    .feature img {
                        width: 100%;
                        height: auto;
                        border-radius: 8px;
                        margin-top: 10px;
                    }
                </style>
                 

                <h1 class="header">Generative AI in PetCare</h1>
                <p>Generative AI, a subset of artificial intelligence (AI), is revolutionizing pet healthcare by providing advanced capabilities to improve various aspects of pet care. By leveraging generative AI technologies, PetCareMate aims to transform the way pet owners interact with healthcare information and services.</p>

                <h2 class="subheader">Project Overview</h2>
                <p>PetCareMate is an innovative platform leveraging the power of generative AI to transform pet healthcare. Our comprehensive solution encompasses disease detection, AI-driven chatbot support, multilingual capabilities, language translation, education, and empowerment for pet owners.</p>

                <div class="feature-row">
                    <div class="feature">
                        <p><span class="highlight">Disease Detection:</span> Utilizing machine learning algorithms to analyze symptoms and diagnose pet diseases accurately.</p>
                        <img src="data:image/jpeg;base64,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" alt="Disease Detection Image">
                    </div>
                    <div class="feature">
                        <p><span class="highlight">AI-driven Chatbot Support:</span> Offering personalized assistance to pet owners through intelligent chatbots powered by AI.</p>
                        <img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxITEhUQEBIVFRUWFRUXFRcXFRUVFxYVGBUWFxgXFRcYHiggGB0lGxUYITEhJSkrLi4uGB8zODMsNygtLysBCgoKDg0OGxAQGi0lICUtLS0tLS0uLS0tLS0tLy0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLf/AABEIAMIBAwMBEQACEQEDEQH/xAAcAAABBQEBAQAAAAAAAAAAAAACAQMEBQYHAAj/xABFEAACAQIEAgcDCQUGBgMAAAABAhEAAwQSITEFQQYTIlFhcYEUMpEHI0JScqGxwdFTgpKT8DNDYsLS8RUWY3Oy4USUov/EABoBAAIDAQEAAAAAAAAAAAAAAAABAgMEBQb/xAA5EQACAgEDAgMGBQQBAwUBAAAAAQIRAwQhMRJBE1FhBSJxgZHwFKGx0eEyQlLB8RUjM0NykqLSBv/aAAwDAQACEQMRAD8Aya12Tl2GKBBigQQoAUUCFFMAgKBB0CFAoEEBQRCAoFYQpiCApisICgi2EBTFYsUCsWKBWLFArCigVnstMLFy0gsULQFi5KAs9koCwSlA+oW9h2XRlKyARIIkESCJ5EUk7HdbMZK0x2CRQSBIoGgSKRKwSKQ7AIoJWDFA7IIFItDAoEEBQAQFAggKBBRQIUCgQQFMVhgUhWEBQIICmRsICgTYYFMjYoFAmwgtMjYYWgVihaCNhZaAsXLQKxctAWFkoFYoWgLFCigVsE0EkAfOkOyz6QWAlxVAj5u2SJntMoZj6sSfWqsDuPzZo1Kqdei/QqitXFNgMlBJMbK0ErBIpDsAiglYJFA0wYoJWV4FRLgwKACAoEEKBBAUAEBQRFAoEGBTE2GBQRCAoFYQFBGwwKZGwgKBWGBQRsILTI2GFoFYQSgjYQSgVihKBWFloCxQlIHKhQs6AeQobBF9w/os7DrMQ3VKBJGmYAblidE9dfCs8tQrqO5tho5V1TdL8/4GMZxLAYaCy21Xk15szv4ojCAP3Z8BVqxTaucqFFx6qxwv1+9gLHynYIHKvVfvC4g+LLAqt6aL/uNPiZl/6f52XadLcPcHzthIOsyGWDrvAMa+VL8HJbqRD8cntKItzAYG8AyIFnYq0AjwI09SGpVlj3skvAnzGisxnQ9yC+FbrAN0aFuD/K/mIojqVdTVCnopV1Y3f6mYu2iCQQQQYIIgg9xB2rTZl9GMMtAxsiglYJFAwIoHZXgVE0hAUCCAoEEBQIIUAEBQRDApiCAoIthgUEQwKZGwgKBBgUCYS0EGxxVpkWxwLQRsNUoIuRIs4Vm0RWbyBP4Um0uSK6pf0qwrmFZTDKynuIIP30Jp8Clcf6thDbimRUrPdXSCx3qs7BLSySYA7/P05+FDaSthijKUkuWzdcC6PLYAZu1cO7d3gv1R47nw2rnZczm/Q9Dp9IsSt7y++DH/ACk9Mbdl2wgIPVIrugjt3G1tWiOSgDrG8CneQb9LFX1BqISlUV35+Bw/F37l12u3GLOxksf60HcOVa+lsnFRiqXBHYGotNElQjYpyotlmyDZZOUem1VOb4JqCvqrcvOiPEir9UdmkrPJhqQPMSfSs2VXuX4nTOpdGeOtbdSsAg+U+B8DWOao0pJqmbnpJwNMZZGIsiLuWR/jA3RvHlPfptV+nz9Dp8HN1elWRWv6l+ZzB1rqHFGmFMYBFBOwIoHZWioGoICgRnsVbu33e4iN83pYMqvaBlmIJ1mAPKsklLI3JLjg0xcYJRb55JGHxTXL6XFQycOZBlRmz6rJGm34U4zcpqSXYjKKjBxb7hcZV3NlWtL/AGvuliykR9IgaDXup5bl0pruLFUepp9hbmBvWhcvWlRWyALbt5mU9oS5BiWAnSKHCULlH6ISyQm1GX1YVu/dZwli7ccMj52e2FFtsvYIOUa5uWtClJuotv5cCcYpXNJbrh8g4bi1+EusrZLaql1SnaZyGlh5EJ/EaUcs9pPhchLDC3Fcvj4fdg+14lVs9czhWtlmdVE5y2insNlhY5Dc66UuvIkur7/Jh0Ym5dNXfH20PYHEYm49u2bpAKOWYW4mG0jMo1iNYjfSpQlOTSsjOOOMW67rv/I7j71+0623uXOryEi4qgFnLGAxFtgIWBsJ3pzc4um3Xn9pkcccc4tpK/L0+qAtY+9NoXrtxENsk3Ldky9wORBBQkdmPoiaSnPbqbSrlLv9AeOFS6Em74b4X1/2WHRFDGIzAicRcIzKVJBA1ynbyqzT373xKNa1cK/xXqaJVrQYGxxVoItk3BYfMQP68qTKpS3otbQkhRtyAAI84YwonmdaTVKyrxHJpdvvffZfqPsCrMhAyyTlIABE8spyt3Tv5VFJNX3LLlCTi+PLZfps/wBfgV+Pw0NIkhhI8toPkR+B504u+SUoqNOPD4+/vzIbLFSIrk1/QfAKEbEuBJJVSeSjc+EnT92sOqm3JQR3PZmKMYPNL4fL7/Q0wuoVLhgVEkkEEQN9RWVpp00dWMozVxdr0PkzinEGxOIu4l97tx315BjIX0ED0rq4I0kjPke5qOAdDutte0YjEWcLZJhXvMFznuUEifjWueVY6Si2/JGWDeSTS7ETph0Ou4RUu5kvWLmlu9abMhOvZPc2h08DroYr8SOVNJU1ynyXJSg9+PMxbiscluakSOFPlvWj/wBRPgSAfuNUy4ZOPJ3Lobbt2YvOAzt7s65FBiQO89/d61T4LceonLMurpR0yztmKanUxow/OazPYnyc56a8LFq/nUyt2XGkQZ7X3mfWurpsnXCvI4OtxeHktd9/3M2wrSZRphQMGKCRWCoGsIUCLjD9GcY65lw7QdpKIfgzA1xs3/8AQezcM+ieZX6Jv80mi5abLJWokLGYK5abJdRkbeD3d45Eacq6Om1eHUw8TDNSXmvvYpnCUHUlQ0prSVhigTYa0EA1oFYa0yLCFBGw1pkWxxaCLY4tOitsdUUUQbJOGsM7BUBJPIVRqNRi0+N5MslGK7scITyS6YK2WvCbMs1uO32hBMRAYEH1NU6jWY8OD8Q37lJ2ldp1TVEceGWTK8Ve9ut3XZlhYGRmSQrkAKZkBhvr3/fD+lSx5o6jFHLC3F78U6fp98EVjeLJKDdS4Xemvv40+L2AxtyQAxDsNWPxn4yo11MeNXwXlsVZpN0pO2ufzv62lvu69SLxA/N2wd5Y+kIJ+IPwNC/rdffJa7WKN+v+itdakQTLHpZxf2bAYdR7pRrjD62vZUxussWI5hI51Vp4XknN9tjqZE54sOCP927+/n9SBwvpHil4bfOJtoqXsJiXw7oQCWWwzgMoMAFQSCAu2wkVz5azSZ9TLBik3OH9Sp+dc1XPqdzDpY4MdJnGeD2OsvW7XJnRT5EgH7q6eL+oyaiXTjlLyTL3jPFG9oLglRbQm2FJUhJCqoI1Uk7kakKNa2umh6CPRitfbujV9HeKPi+G8Sw+IIdbdgXkOZny3EZtnYliD1abk7MNtK589s0JLa3X39TVkl1xtnJ741qOXkjDgTDGHQ9zL/5CqXwWLk7h0d7WIsodsyD0EE/GK6GeCjiddkcrDmvIk+7OicCvtefFM7HKuIa1bUErlW2iBjpqSXLme6K4U2opUdiNybKrp/h5sKx1a3dyz3q6z+S+s1p0cvfrzRh9oRvGn5M56wrpHIQ0wpgBFImVQqBsLboubYxdk3YyZ+e2bKck/v5a5XtxZn7PzLB/VXbmrXV/9bLdPXix6uPv/ZddK8FjWxLsFvMk/NlMxULAiMvunvnnXG9gaz2Xj0MI9UIyr3uqk2+/PK8vQu1MMzyN067UTuE8IuPetNxCHbqX6u22pItuI6w7MfnNvKdjWD2h7Tw4dLlj7M92PiR65R4XUn/T5L3efPjlFmLC5TXjbutl8PP6jvCGv37hs4vBotqGn5opkI2yud+7TzqHtFaXRadZ9Fq5PJar3+rq87j+/wAHuGJzyy6ckFXwqvmDjWt4fBWmS3buHrWCM4zD3rpDmPe7I08weVW6WOfXe1ssMmSUF0RclF12hcV5b81v27sjkccWCLST32v57gXb638GcWbSLes3FgqsBoZDBHMQ2x5irMeKei9rLQLJKWLLB7N21alw+zuPKrZkJSWXB4tJSi/2/cPiXCRi3sX7Ai3dAW5EDJlmZjnEjzUd9Gg9rS9lYc+l1crnjbcL/vT4r0un8G/JizYPxEoZMfD59Pvgl4c2MRi3XKhWykW1gQzT2mj6UaADbnWPP+N9n+yoTc5KWWVzdu4xa2V79N8t1d7ehZF4s2oapVFber7v1CdC6XLd22LjZTkC4Z7OUwdesfsjlsfjRHJHFnxZNPl6Fa6nLNHJ1K1t0RuTfxS+XKTTlGUZxt1tUXGvm9vzB47ilsCwUs22coYLLIUALOgiSdNeXrVvsbSZfaM9QsmacYKfEXTb97u7pLyrd/BENXljgUOmKbruvgDwrFLcNy+cLvC5kQXMrBdexvrIOk1f7T0s9OsWljquLk4zk4OUW9vf3W1VTrzSK9PlU3LK8XpaV068ufoHxDCXLtoEdW3ziCTZaw4khY7W4lh/7qPs/wBoafSatxn1xfRJ0siywdLqvbh1F/wnYtRhyZsVqnuuYuD5rv23J6hhdFpkXKdwuH+bAPI3GaD6D0rlucJ6OWox5JdSunLO+ttd1jjF/HeXG91uaV1LMscoqvSHu/8Ayb/0N4AdXinsKFCGXGmoJVdAe7fStPtFvWexIa3LKTmqi99nUmra4v1KdP8A9nWywxS6Xv68LZPy9ArD3WvAXLYCi40HJE9l41nXStGX8Fg9nTlpc7lk8Nbdd1vG9v7WuO1cFMHqMmpisuNKKk9+muzrfuTBZUZ3RQXz6yJjyHfB303rOtZkzT02n1OWUMTxp2nXU/WX5b/qy3wIR8XLignPq7q6+CEa2CpN1V94RAjMJgAidd/vrRHUfhdfHDos0pwcW5Jy6lGk3afbi/15RF4VkwuWogk7VNKr37rv97EfiONFu8BkWMolokwSdF+/41L2D7Nlr9B15s0/6nSUqrjd82/jsl8Sv2hq1p9SoxhHhW6t9+OP5Cu4FTdR7aL2kZiGHZG0HKNz2qxYvas8Whz6fU5JvoyKKlF+8171rqfC917781TRfPSRlqIZMUVvFtp8dt689/Qd4nwq3ibHVXlVla2R7sFW1GZQdUOugrNqtVPQThl0+Sne6WV5LXlL3VH9+3Fm7DHrScl2/wAa+m9r4GP41h+r4Ct1v7rAog1+nfFqz66O1dz2O1L2trP/AH/l1S/ZFk2vDRxjBXWtXEuQZVlcA6TlaR6GImvY43uYMsOqLi+6Ok2+hl/EumLwSJes3Ne0UylW95HVtiIiI0yjmSBoefHDabKNBkni92Ub+n+/qF0q6nhmBuYC2UOKxLKcTkYMLVpCWW3IAAJJ2AGjNM6FqY/9yXiVUVx6vzNWbKpbJV9/r9+pyW60mqZu2TiqQBMa1U+CaO68MBs37btsrIx8pg/cDXUk/ExNLyODvizpvz/KzoXDbRsXb+ha3fuC8pEQr9WiOmp5lA478x7q4E49aXmj0CfSyt6eXSLCqRBuXcxHcFWI8/d++tGkj7/wRh9ozrGl5s58wrpHHTGmpkgIoGVIqs3BUCLDD8YxCDKl+4ByGdoHkOVYcvsvRZZdc8MG/PpRNZskVSkxq7jLrMHe47MNmLsSPsknT0q/HpcGODxwxxUXykkk/iu5W5ybttkm7xbEOuR71xl2ILtBHj3+tUYvZmixT68eGKfmorb4eXyHLNkkqcmA2LuFBbZ2KKZVSTlB12HqfjV8dLhhleaMEpvl1u/i/kit5JOPS3sHbxVwIbQdghMlZOUnTceg+FOWlwyyrM4JzWylW6+fzZHxJKPSnt5DuGx11AVt3HVTuFYgHSKjm0OmzzU8uOMmuG0m0KOWcFUW0hu0xUgqSCNiDBHkRtWicIzTjJWnynumVW07ROfil9hla9cI7s518++sWP2ToccuuGGCfn0onLU5pKnJ/UG7iXeOsdmyiBJJgeHwFaMGlwYHJ4oKPVu6VX8SrJlnOup3Q7hsVcT+zdl+yxHxA3oz6PT6j/zY4y+KT/UrjmyY/wCiTXwY7exl14z3HaNRLHQ98d9RwaDS6e/BxRjfNJIWTPlyf1yb+Y8cfdMTdcwZEsdCNj51VD2Zosd9GGCtU6it0+V8PQJarNKrm9vUs8JYJPW3mYtoRqc22mo1mOQjQjXWKlHTYY4vAhBKHlSr124G5vq8TJJ9Xx3+/v0LT24kwVMCYOZZHInv28azR9j6OCajijvs/dW65r6kpe0cjlTb29fv9SNeXUvaZlbUsJaTpPnpqYM89eVXz0mCeNYcmOLiuFSpft8irxJdTyY5NS77vf78nfx7FdexLsQWdmjaSdD4VPBotNgTWLHGKfNJK/j5lU8+XI05ybrzY3fvM5liSdpNWYNPi08OjDFRXNJUhZMk8j6ptt+o57Xc0OdtBA1Og/oCqf8Ap2k6ZR8KNSdy91bvzfru/qWfic1p9b2434N7wEC5hrZfUkGTzkMRuPKuVm0Gli/DWKPSnddKq/gel0k5ZMEXJu33vcy/yyoLfB7/AFfZ7WHgjQiL9sjXflV2nw445nOMUnLl1z8S9RUYKK4R84PnPzjktJ3JLGd9SfKuvHYok7J2B41etKVtXbiA7hHZQfMKda0LJGt0mUvH5EDE4gtvVeXK5FmPGkRDWRl5e9EeAPiry9n5pWBuMRpAMlB3k7eEzQotkZTUTuNrCq/v+hG4/WrlkcODJPFHIqZquFXHt24uXVIUe8VjKo5E5tY76wZF1ytLk2xahHd8GJ6TcV9ouSJyLISdz3sfEwPQCuhgxeHH1OFqtR407XC4KNquM4ywpk0BFBIqRVZtLLo9wv2nE28Pmy5yZbeAqljA74U1DJPoi5EoQ65KJOxPsB6y1atYkOq3OqfOrl3RWIFy2F7IJXWNvDWorxNm2qHLw90k77F1xXolY9qOFsYhLdwopS0wuOWbLmOa5skwYGunmKrhnl0dTXzLJ4I9fTF16fyROF9EGuqs3urdywCtafLKkiDc90+7ympSzqL4/Mrjp3Lv+X+w7PR3DjDPevYko6Xupb5tmRHHvIQBLnftAgUeLLrSUe1kfBh0OTlVOuPv6j+M6P4YLhR7QLTXrKNqtx87vEGBpbXXmefhRHLO5bXT9AnhhUfeq167/sRr/RrqVzYu+lgF3ROw90vkMM0LsvifhUlm6toK/wAiuWDoV5JV+ZNwvRa2vtC4m/lazbzjIpZcpErcJjtDcZRB0OtRedvp6Vz90SWmiupTlwr/AJ/ggcG4fbu4tLGcvbZiMwBQsAhbQHUaiKtyTlHG5VTM+LHGeVQu19OxZ4Th2FxFx8PZW7auLnyFnDo2Q7OIlZ8P963PJCKlKmixYsOWTxwtPf1WwVroo8DNcCuUzwbbm2oiYe97qmm9Suy2+O/0ILQya3dOr4dfOXAzb4ExbDqjhhfWVbLGWPfBE6lal4ySla4KfwrcoKLvq7+Xn9Cw4f0blkY3MyNcITLbdg6o0EsRoimNyaqnqKTVb15/dlmLQ203LZvbZu68/JFvb4RIt9oFy1zO0kqQCSSPMn8qj49N+VKh/gnKMd/euVvtS5/P9iQuBDEKjZhmCtp7pK5hII1kc53jQ60vEaVyRFaZTkljlaun6WrWzW+3e+atPcgJwvMz9XdBdCMy5WGXtaEFveEifjqZq2WbZdUdmZ8ej6pSWOduPKpqt+VfP/O7sj4ngK5ruW+g6tpdSG7CHWZ5kDkKjHO6Vxe5dPQR6p9M17vKp7L77DY6PMSCtwNbKZw4ViYmICbk+FP8Qlyt+K/kS9nybtSuNXdP9ObC/wCXjJ+dUL1bXJZWQgKQIdDqu++uxo/Eenegegf+W1N7prjzXKL/AIJjLduwg6wOnWFAwVlhjqFKnXc7+NZc0JTm9qdWdLSZ8eLDFdVq6umqb7VyQunuHtYzDXcAXKliksBJQo6uDB0YSoETzqWDBJ1LsPVe0oYpOCVvvzt+Ry0/JbaH9pibzeSoPhM10I40YZe059or8/4CHyb4Ie9dxB/etgfclTWNEH7Szdor8/3D/wCSeHD+7dvO6/8AlIp+FDuQ/wCoaj7SEvdHMDYttfOGUW0IzMwe5BJgaMST8KXTiTruW4s+pyq7/RFl0T4nh8U/UYZtVWYyMixIELI8az6jNGCOjg083yXV3H9XlyqDKI4Jn6ShtR4TG/KlGKmrMuo1UsUulIhY3iNy5o7afVGi/Dn61bHHGPBgy6jJk/qZXvUyCGGpkkNsKCaG6CRUCqzcPYa+1tluW2KsplWBgg+FJpNUwTadou36W4shu2gZgQ7izaDsCIMsF51V4MPtk3nnX8Ee5x2+2IGMLDrhENlWNFyjs7bVNY4qPT2IPLLq6+5MXpXi+wc6lkJysbVssATJUNlkL4Co+BAfjzBwnSLEIbkMpF1zccNbRl6wmSwBGhpvFF16EFmnG677kheleK7EshyKAk2rZyxsVldD5UeBD7YvxOTb9kBY6RYlQQXDgsXi4iXAHOpZcw7J8tKbwwf8EVnyLvfx3PYfj2IW697rMz3BluZlVgy9xUiI8qbxQaUa4IrPNScr3Ylrit0XxiQVFwbEKoA7OTRQI93Sm8cenp7FfjSU+vv9of4p0yvW7Ts7qgIIYpbRWefoggTJqp4scN2XRzZ8z6I9/JUYe98qGP0Fs2lCCLZa1buXEA2h3B19KolTfkdHHj6IpPdru6GuD9PsdbttZXEHK5JMqhKyIbISOzI3ipUpO2JQUYuK4Zr+i3TW4AtlysBpQMissk/RkSpn+pq5wjN78nPyRy4I/wDb3it6auvgbn/id05WD6AsydldQTswHd7pHgO8Ulihumvj9/mZZ6nNaalxbWy7+fw4f8knBccfOudcyqSTlWDsQIAETqNZ+FQngjW3I8Gvy+IupWlvsvivKvz+hHu8Qu6gMFGbMxCrJUGQWIHaO3noNTT8ONXQePlurre26XHa9t/tWyoucVuFrpBA62Q4gHSToO7erFijS9DO9TNub/y5FtcZvKECvARSoGVSCpiQwI12oeGDu1ySjqssUknwq+XqSLHGn1DwEZWUqiImjRmiBvoNaHhjyuRvV5OHw000kls+exHONZU6pT2c4flOaBBnfkKm4Jy6vkZ4ZprH0Li7+YWN4rcuiHI3mQqqSYiSQNdKjDHGHBZm1GTKqk/ySIU1YUbiFqBiFqBpFZ0uvxw66C0BnQKJjMwKzPfC61Gk8i+B1dFag/Kyg+RzDo+IuO2Y5QgUKzrqzEycpGnZ56Vi1b2SXmdrDtbZu8TwjGMZe0ZiAM1vadgAfGtccmKKqL/U4M8OoyPqmt/l+41e4BilEmw5+zD/AHKTTWfG+5B6TMt+n/f6FXeQqcrAgjcEEEeYNWJp8FTTTpjBpjQ21BNIboJFOKgbQhQIIUCYYoIhigQYpkAxQIIUCY4tMgxu7j7SEB7iAkwAWEz5b0nJeYLFOXCZQdLMQrkoCCLZIaDIzjQieZG3xrJll1S24R19Hh8PG2+X+hi33qBcKjRTsRdcOxGYZDv31NMVG/6G8fuFTZuHMya6z2hsDI1DDaQdREzV8feW/JxtZh8GXVFe6+3r/r5foaxOKLvkM+dv87dJwfn+v7mRZIp3X6f/AJBxvFWuAAgAAzpM+pnXn5SYilDH0sebO8iqvv7/AIIAbxq0ooTNQMUGmIKaQjwJOg1J0AGpJ7hQSSvYtn4DcVQz3Lak7KSxYmJiFUyY10mIqjx1dJM3fgJqNtpDmH6PXMjXHGysUQMAbhA0GaCFBMawT4UpZ96iTxaBvefHl5k2zgMguqqh7luytwBVyi5cYXAEUmWCTb+sWltwNKzylJ8s6WPFigvdir+/mch4xieJY237PessVBJE2ShDls05n2+rEgR4ia3LFFr3Sp5FjfVJhdG+g11CWu3mthhDJaYhmX6rONhuCBO+9NaeMdyE/aHVtFffwOl8Fs2rAy2lCDSeZP2idT60slyK8TpljxDpXawydZcceEmPv7hvWHLBpHT0762U2H6TLjcr4u1ZXCvmW25cjEhhHaCZdF1GgLRKzvUIRywfu8ks8cE4vrW3mQeJ38Jg7RvMvtHbAQkwCC0AhZg9kE66GOVb2pyjfBx8UMfi9HKX3waDhnDrOPsm6lq2i7JcQZGJgEwFEECY13II0ia56z5MT3d+h156TDNbKvVGIx2HNq41p9GUwfyPqNfWupCXXFSRxJxcJOL7FAKRrCFAghQJhCgiGtAhwUyIQoIhigTMz0o4qw+atsQPpEaek1lyZG3S4Ong06hHqkt/0M/wjhvtFzqg6oYJEgnNG4EeGtRhHqdEsuXw49VWTcS2RrttzmYXHloAzMT2jHiZokqbRZjn1QTI2P4RcRVcgHMJgEkqD9YR36c6oWWLdF8sElHqIuGwjuYUVJzSIRg5cGv6MdEescdbcIE7Lv8AE/pVMtRXCNMNL3kzqOP4Lh8Nhh1VsKxZRm3Y6EmSdTtVmkyTnl3fY5/teEY6eku6/wBlMrV1DzIWakB6aYHpoChc1AhZoAsuBaObkTkWR9o6D7pqvJxRt0Ubn1eRQcY6TXTjrVhSAbt2xaBgMFtu8aA6fRLHTWbYM5ai1GOOzoRjLJk34+/3/I6zjLDHtDu2rDGaWxtljfJT33OxrREzSKTGETrW3Em0crUSUWVl7FgbVoUCmDIVziRoeNGqLo510+4g1y+tsnsoi6eLEkn4BawZv/JXw/M6ml/8d/Eh3uK3Xu2kuEoq5AoE7DtroTzZiZ8aLqe3mv8AQ5RvG299mWfH+Ju+HtWQAtu2LeUTJ7KZQWbnoe6tM1UUYsEV4kn3d/qds+R+8G4XYA3U3AfPrGriav8A8jO1i/oRYcX4Tae8zsBJiZA+qB+VPHllGKSKcmGEpW0cXFdU5wQoEEKBBUEQxQIIUEWGKBAYu6VRmG4GnnyqGSXTGy3T4vEyJHP8fc5b957zzrIdab7Ezolhy2Ktx9HM58gCPxIHrVmJe8ZdTKsT9S36U8CfrTftiVcjMOattPkfxqWeNe8VaLL1JY3z2LF8FmyOJJFsI6knkNGXlrGv9E8fq3PRdOyGcLggjbb1JzsI41E0uD4BeL27tu2Llo+/84yMp75FThJVuyOSLT2LXHO4VLbMzAKSMzFjqxGpPdEc/vrfoYrpc+9nnfbGSXiLH2Sv5uyKGrccZoXNQRFzUwFmgDwNAhc1IC24K4W3ibh2W2p+8n8qzZ27il3Z0/ZyXvt9kc+4OLAv2cVdH9netvcbU9WVuTnYD6JBOuwI1rTqIJRafy+RLDkn4ir7T5+nPqfQKXfon0/SuQ49zsp9jJdLuMLZtvdbRUBJIHaPIBfEnQedb9NjXLObq5yk1CHc5O/SvHXmm1bRZBYJkuXnKbScmsT9KANdK2dclvskVR9nYu7bf0LDgnHxiD1dxQl0CYBlXA3KHw5g/fBi+E72fJkz6V4fei7X5r4li1qrKIKZgum/Dn9oDqpOe2CI17STI/hg1ztTifXa8jraLKvDp9n+o9wDoscRl6lXuNK6orRacwwzGMrLoZg5gGUxvVOWUY8/E0R6pL04D4phCEKEarKnzUkH8K3yXVA5sH05Db/IfxC4Otsq4gEMFaeY1g6x7o0j4azx9WlSbR2NPbtFlx7jWIOIuw5WHKwANMnZ/wAs1ow4oKCtHLz6ibyOnRixV4whQIUUCDFAghQIIGgQYNBErekOIy2iOZ/UfrWbPLhG/RQpSn8jDOaqNJpOhWCdna4CwWCsgkSx15bxUoya3ITxqezRcYrGXQxs3REEETuw5GdJH6VTqMzkuku0mlhCXWuSXhr4zCsDR1UyTfw8mkiRpeHYx7VrqFLBroIRlRniImQvn+PdVsY2RcZS4IF26YCkhsuYBoiRMjST4/Guvp8XhxrzPIa/UrUZLS42+I3mrQYWhQ1MjQuagVChqAoXNQKhZpBRYo2XAYxu8IvwDf6qolvnxo6ekVYMkvv73OYQ2dcrFTO6kg924866U429yuDqLO88BxhuYa2zGWygMeZIET6iD61xssFGbSOnhm3jTfJlflKw5uYW4q7jK/8AAwc/ctbdKqMOfKo5Yt/D6qjJ8HwVt9Mpa2S7FR12XMWt+z9Z1PbCCxITkGDDvroYnXent5XVO66tr6ufQsyyl0+79/Qp+KALjrPVFiReAk++fnGEP/i6o2g3jM6g0pJWq/LjjevS7oWSX/Zl1eT/AINndA5VJnFwttWyo4+4CWxpmNyVPNQgJYj4rVORWdDC2mzoXya8KFiwCWaCMxBZ4UbwBmygDXQAV53US6slI9HBdMLZzLpAgdr1wCA113HlcJb8Sa9BjVQSPOKfVJy8xj5Mcb1OPCzo0j4GR9wNc3Vw91+h2dJP3vijedKODXWxV17Y7LFT6lFLffNGnyxWNJmPU6eTytowQrQRDFAmLQIIUCCFAghQINaQJXsUn/DL2OxfstmBoZZvdRFIzO0cpgRzJHfWFytuTOwoqEVBG4wPyccPtgBxcxDKO0xcAE/9pdh9qfOiwLGxw3DJ2bYKRspUKI7tNKbsQxx3gYvoAoAddUb/ACnwP6GoTh1IljydDMxg+GMxykEEGCOYI0IrCzpLiy8xvD3w5VLiyCoIM79+UjumI/UVtw6SGSF3ucnU+0cmHLSXu/r8yTb4kotMmWWIhSfonv8AOJipYtFKOROT2RXqfakJ4XGCab2+2V010Tg0ezUBR6aYqCDUxULmoFQuakFHs1AUT8W0cNu/4r0fBF/WqoK9TH4HQwutLP4/sYPBWc19R/XP9K6M3SbKI7qvNnWMJi1statHZlAY90nsz5Nm9G8K5PT1JyNuTMseSMO1f8HuMKZM1r07VHK1ybbMHj+izhi2GuIFMxbuKxCZjJ6t0IZVJ+jtrWvfsyGH2l0rpypv1T/Vf7F4L0a6l+uvOLlwCFhQqIP8I9TyG5561OMe7FqNc866Iql+bLRzrTYY1SKDFnrsatpdQgCepIZ/9PpWXPLpg5HV0sLaXmdS4ziPZ8DkGjXB1Y8iO2f4ZHqK4elh15b8tzp6/L0YqXfY5zi0BR5IHZ3PmI/H767kJbnCgjI8PxC2cZauO2VVcZzvlWYJganQzVOeHUml5HS0zaps+gMHxpWRSbF3960wJAMA+RGo8CK47xtcM6Dmu6OLCuscsMUCFFAghQRCoAIGgBLt8IpZthUZNJWyUIOcqRpPkqwvzGIxZEG9dyKf+nbE6fvuw/drn5Hwjrx5NFhbgF6DEH7ql/aQ/uLjFYBX94Anke/wJH41FSok0MWsEAIHp+lSsraI78OTrM40bTN4kaA+fL0quWK5dRdDM1DpJPSPBi5hGzDtW1zr3gruPUSPhVmGTjk+Jm1cFPE/Tc50DXROFQuagR7NTELmphR7NQFBBqBULmpBR7NQOidxgeyYYPiiwtudUChlDBSV6wEzmMECBpzIqtS97qXbubMeCXT0t89jE9DOJi9fLO1qyVWRm7QdyVVVCmIEtvJjuNTnqHKNUX/hljap35bf7/g3PFrztcJuLlMDTwAAEcjtuPGoYunp91mDUdbyNzVPyLnA4jr7Op7dsAP3lfov+R8R40RfRKgmvFx33XP7kK6sVvhI5GTHuRLxq2wxxpkHF3xbtvdP0RoO9tlHqSKT4N8F1SUSL8m/Djcv9a+sSSTzYnf7j8a5ftHJUehHe0MLk5+Rf9MeI9bfyKezaGQfa+mfjp+7Vekx9EL8zLrcviZaXC2/coLlsZC1wqqSFLPostMAnyBJ5AAk1plJIzQxyk/dMXxTht/iGLb2Sz2Sez9FEQHQmQMi9wOp7pkDHluKTkdrDT2Ro7nykcTtk2xYttlJWVTrV0Mdl1BDDyNQWKNdy1zt8L7+ZFFbTlhCgQooEEKBMIGgQ3fxCoJYxSbocYt8FPxvHKyQmuu3eeVZ8srpG7T4+hNs7XwHhww+Es4cR82gDHYFt3b1Yk+tZJbs0xdEPE6XAQJ18vy/SrorYrb3NMGJQEctf1FVVuWN7BwHXMND+B2/Wjhi5Q3g8NEz3z6j/enKQooXiylrN1FEk2nAHeShApQ2kn6hlVwa9GcnBrqHn6FmmKj00BQs0BR6aBC5qAo8GoCjRdFeF5ycTdgW7e06AsNZPgu/nHcapyT/ALUacGK/ffCMz0u41bv4i4zdu1YEEbLLGBaA72IlzvlXKIhpvw49ty3JNqkuXx8PMyXR3BEY/CXWjK2KtysABTmBTQaRIPwqvPhcPeXDs04Myl7vdUda6bt84hIIOXckHMukERsJzCO8Gs+l4Zn9opda+BR4DGtacXF5SCDsVOhB/rurTKNqjBFuLtF7jHHsntYIzkMRbmJKsVgHfWO7nVcc7WTor5l/4FZMXidXntRzrHdNnUx1dsebk/pWt5lHuiEPZ992VF3pBiMUy2gEILCERWJJmBoCSd4076reeT7o2Y9JDHwnZ1fBtYwmFPU3Ab4IGUgAgkwTETIHeeVc5KebLc1sa55YYcVY5KzOooOZmMIoLO28KO7vYnQDmSK3t0cqEHN0ZvG3mvlrt8m3h7J0Uaw06Ig2a4Y1PeCTAWpqKUb+3/CNK2aiv+P5Y7wO9iMWfYsMOqtuZuBfoptDvu5I3nfYAAEVizOMfflu+xuxRcvcjsjs3C+idm1aS2FEKsf71y5SlJ2zoR6YqkcZFd04QVACigQQoEEKBFB0qu+4PM1XkL8CIPCrRu3LNpd2uLPxEn0E1me7N3ET6HwN3Nbg7rofhv8AD8Ki1uRT2KziixrUoiZe8MuZrY8RVUtmWLgj4LFFGhtjo3mNKnKNoqjKmXNuNxzFUlwPOhjOS8WtZL91O644HlmMfdFdSDuKZwskembXqyLNSK6FmgVHpphR6aAoWaQUWfR7hD4q7kEhF1uP9Ve4f4jy+PKoZMnQrLMePrdEHp/0zDEcO4cQtu32WuA6Su+U9w+t36jWDUcOJ3b5ZslVeiMXaXRbazkBkDm7fWI5Durowjt97mSct23z+n8mu4VwPJbN+6SGDWisQCGW4jgCfsn0mqtRO10kcU3F9S4LHinEWvv1jxsAANgo5D1JPmTWaEFBUhZckskuqRDmpldE3hOHdriOiMwW4hZgpIEMDqdhpUJtU0WYovqTS7o5v02Km8crK0ZAYZW1CKDqPEVHK04I6WC1NidCsSFxVuWAHWWzOmnaHP0qu49EvgXU+qPxOo8T4Vf6y45tkLLOSSoAUk9oydB4nbnU8eSPStzm5cM+tuu5nGdcQ85ymEwxDvcBKtdvDbIdwd8v1Vk6Foq+Ebe/2iV+FGlyVtm1c4liFs2k6vD29ERRAVdpj6xj7vCqdRnUFZq02nb557nTOEYS1w24llLarmPbUwbl4lUVOq7RaC7gAsAJtXQd1NcuTeT3pHR2htEvOIdMMLbuNbZ2JUwcqlhPdI7tqlHSzkrKparHF0caBrqnNCoEKKACFAggaBGd6Ue8v2fzNVZDRhLb5KsEGxFy621q2I+07afcjfGqGjT2OtcOYq5ZtFaBHnt+dDVkboc4ra0NRXJJ8BcExixk10+FKcSUWe4ictw9zQR+f3g1bBXEz5HU6J3D8bpBqqcO5bCfYnPdGpH9a6VXRbZz7p1hsuIFwDS4oP7y9kj4BfjWzTu4V5HM1cayX5mdmtBlPTQAoNAUemgVEnC4R3KwrEM+QZQSS0ZsqjmYE9w5kVGUkiccbkUD9IcYue3bxTIhj5lUAzLcBIU5e0CV1zyTDLEaCq6t33NyUFGqpBYno7bVEuYZpz5c9tiC1ospZQQCZUgGP6jZgp2nyYs+WvefBfcF4KlleuvH1OpnuUcz+HhU8uWtkZop5N3sh3iGPNwgAZUHur+ZPMmsq82XSd7Lgh5qZGi56KvhhiEXE9ouLnVJEgm2oZ2edAACAJ3J8KpyuT92Jdigqc5cI2+J4tby5EtWwo2HZgegpQ0zu22LLrVVRivqY3j3DsFcJvYi3aB0zOxWO4d1bYw7MwrUZG6g935fsir4df4dZcNZ9nDzoUylvSJNScYVRojLUcuyR0x6QnFG1gUYWrGXrLp0toqrmCm5oOdtoUCJg91ZceGEJNrd/oa1lnJXLbslzb+X/BiLWP8AbjZwGFXq1E9lmE3G3a4TAkxJiNANBoZWTURimacell12+Tt/RDo1awNkDTNEsx01jVj3CuROcskrZ04xjjjSM50o6QqbpfDsC0AKwgxCkF55bjKORXN3Trw6d/3GHPqVXumPmtxzyuBpFoYNAC0BQoNMQQNAjPdJffX7P5mqcpow8G0+RxVyYgus9u1B7yFfQ+Ug/vVQ7NBtOI3ydNh/W9WRVFU3ZJwuJ6xMre8og+I76jKNMcZWqKoY1bLGO0w5TovmeZ8KfQ5ApqJeXSL6o85WCiVO0T4bGZ+FEX0bCnDr3HbOEIBmNuRqMpWOMKG+Is4IXq7jDdiJAnuzRy/qKcUmuUEpNPhsXjPDrWLtKrXBbZTKto24gg6jQwOfIVXCfhsllw+LFGK4jwB7W1y1cHergH1DR901ojqIPlmOWjyrhWQBhTzZR4SJ9OX30p6qC43LMfs/LL+rYE5QYcOmkyQCI7yBrHjVK1cu8TS/ZsKpT3+AN1cvMHxFa8WSORWjm6jBPBLpmJihc6sm0Wzm1cCgEgEQxfLrGsKD3hd6teNdPV3K8eZ9XT2/2aP5Muj0IuLxJksFW0GliSNc+UgbE5Ry0B10rPlbXur5k5zhKSbaq9u+/wAO/wA9kO9K2s2sZcudl2yKoUaHPJZmuEaAarCjWcx0zTU8MpdCrYqnBdTTd7mdxGIe4czSe4AaAdwHIVMb3Gxab6rfA0BQow7/AFG/hNFiohcOvFOKWluKw+YZVmRE9Y2xGmoqUF7xPM2tK2vP9jbXLg8fj/6rQji+JfYwnyi4tps2UBObOxHe3ZVfxb41DLJo6fs3Gn1S+BA4cqWVVsvWPczKAcysSeymSCOzJznVdFEmGis8mzppJujQ9E8RhlQtiQvVrHzhUL7xITrFGhnKx7Ekhfd51my9b2izViaXKJfSLowq8Q4biuG2epa7F69b2W0LT28zv9UEOVI0mNpJqGKXVjkp9v8AZbJ00y36ZdKDemxaJFqe02xueH2fxq3BgUN3z+hh1Goc/djx+pki4760mUHNSoZABpFhJwWDuXWyWbb3G7lUtHiY2HiaTklySSb4NDheg2NbVkS39tx+CZqreaJNYZFla+Ty59PEIPsozfeStR8deQ/B9RjiXQ8WgMru559kAfnVkJ9RXkj08GS450butqtsk7alR+dTlDqIxyqPJreguBGHwYRlJu53e4qxMkwskmIyKu01neOSZpjljJbBY3HuWPzbf/n9aujAplMDCcRdWDZG8RpqOY0NSeO0VqdO0HjrYVpG2hnvnUH86SVok3TBTiBmQxHqfSe+l4Vj8ck3ePvkyaEns92+kj47fhSWn3sf4lcE3G9Jgtt2J0yt+FVSw0i2Ga5KjD4HGYy/rZVmExIgLP2iQKzR09m2erjHlh4y1i17LjMRuAHMfvZcp9Cas/D0VrVqXAxYwuJLDOjqveuZZ9SNvSjwUC1KLDEYZcqrcxS5ogrD3OzzjMoZW8tPA1KOBeZGep9C16L21sl1HXMpC5DAXQfWzLr8OXjpOGncZNoxazXQnjSfK8izx1qwdbtt2LTGYgaCNDlAnkfQeu3G8myTWxw8mphFN0/qWXDMeucBSCVXRRHZI2WOQURpzJPpHJi91mbFnakpy5Jr4gA7VBQNMdQIMQKfQWeOmL19HQHiidfR0j6zO9I8ALl6ziEUdbb0MkgPbJkqSNjOx1iTpVmO0mJ5404S4IN7rxtaB/fH6VdfoZ14fn+RTcaw9xgt04di6e4Q6QpLKSxOvJSIj6XLcQy3Xuo2aNw6+nq2fbfcxd7jTm69zEfOuVCne0UGoe2ijQZpXb6BjsyQMSyVydxYV01Em8OtXb1zKof5wI7wsqtnKSOz7pbKTCxADaaDSXWmur7+/MfQ1sjsnAOIlznuWeraAsLbgBBMDMANNSYEak1z1jldGmU4pWXPtAPfWtxMEZCEKd1B8wKgWIT2a3+zT+Ff0pWydHDhWsyF1wHpJiMJIsMMrGWVlDKTETyI07iKhPGpck45HHg0tj5SH/vMOp7yjlfuIb8ar8D1LPH80Tk+UHDn3rV5fIIw/wDIVHwmiSyJg3emeDbd2Xztv/lBqyMGiubTId3juDba8vqrj8RVybMsoWFg+KYUNPX2xpzYD8aJW0PEulkhsThm2u2j5XE/Woq0WtJnlt2DsynyYfrT6mRcUM47h1u5AkwBAh2H4GpRZCaIw6PW++5/Muf6ql1FfSIOjlkGSs+ZY/iafUHSSxwKzH9mvqJ/GotjW3ckYbBxpJjuk0rCSQvE+Gi4oUvdTxt3Xtk+ZUiamt1uZp5XjexV/wDK6b9fiuf/AMi5zEd/+1HQiv8AFyXZfQMdGRyxOLG39+3IRR0IT1cvJfQlWujZH/zcb/8AYJ/EVBxRmye0ZrsvoE3AQNXv4i7/ANy5mI8AQAQN9Ksx+7sjDm1kslNpfT7RKw+CRB2ABGogRVnV2M/U27bJF27OtRUaNsXYitTouig81RosQs0DI95NZqUSpx3GLkcyB6ipWiSxt9iLiFtsIa6ohgfeXkZ1moTmq5N+kwuMuqu36mW410fw15na5fUs11WLZrclQGAXT6OvrAmsculuztY7jBRSLzB4i1bYxiEyyYGcaAknkfGoVGqL3Jtt0X2D4/hlIzX0iO/n6VRKPkTTH36UYIf36+iufwWpKypxGm6X4If3pPlbu/6aNw6QP+dMH9Z/5bUqY+k5SDW454QNAgwaAJli1KT4n8qiy2HBCv2YpoTI5FSIMSpIiJTECRQAmUd1AChyNiR6mkOxfabnJ3/ib9aQxfbrv7W5/Mf9aAoT/iF79td/mP8ArUSXShDxC9+2u/zH/Wk2w8OL7L6Ce33v213+Y/61G35j8KH+K+iBOOvftrv8x/1pW/MfhY/8V9EJ7bd/a3f5j/rR1PzDwMX+K+iPe2Xf2tz+Y/60dT8w/D4f8I/RHva7n7R/42/Wl1S8xrBi/wAV9EL7Vc/aP/G360up+ZNYof4r6IX2m5+0f+Nv1pWySxx8l9Bevf67fxH9aVsmoR8j2cncn4mgl0oXKDvSJINVHcKVDsNRQMdWlQxwGigCFID1AHqAFoAhA1sOaEDQIIGgRecJSbR+0fwWoPkuhwR8VZqaEyBctVJEGMMlMiNkUxAmgATQAJpDAJoGITURgzSYxCaiSQk1EkeoASaRIWaAPTSGKKRJBTQMIUiSDBoGGDQMMUDHBSGOCkAa0DDFIYQFABBaAFyUAVlazmBCgAhQBoeBf2J+2f8AxWoPkshwBiakhSK+9U0QZFepERlqBDZoEAaAAakSANIYhpDBqJMQ0hiVED1BI9QNHqQxRQMUVEkEKBhCkMIUyQa0DHBQAa0hji0gHFpDHBQNBrQMMUAFQB//2Q==" alt="Disease Detection Image">
                    </div>
                    <div class="feature">
                        <p><span class="highlight">Multilingual Capabilities:</span> Providing support for multiple languages to cater to diverse pet owner demographics.</p>
                        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS2HLSGM3v0JUKdqfzveyfaK0c7JxgeHCxUsmaFryaXQg&s" alt="Disease Detection Image">
                    </div>
                    <div class="feature">
                        <p><span class="highlight">Language Translation:</span> Facilitating communication between pet owners and healthcare providers by translating information into different languages.</p>
                        <img src="https://img.freepik.com/premium-vector/isometric-online-voice-translator-learning-languages-concept-e-learning-translate-languages-audio-guide-artificial-intelligence-chatbot-translator_589019-2534.jpg" alt="Disease Detection Image">
                    </div>
                    <div class="feature">
                        <p><span class="highlight">Education:</span> Empowering pet owners with knowledge about pet healthcare, nutrition, training, and overall well-being.</p>
                    <img src="data:image/jpeg;base64,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" alt="Disease Detection Image">
                    </div>
                    <div class="feature">
                        <p><span class="highlight">Empowerment:</span> Equipping pet owners with tools and resources to make informed decisions and actively participate in their pets' healthcare journey.</p>
                    <img src="https://fullslice.agency/wp-content/uploads/2024/04/dig-labs-1-1024x496.png" alt="Disease Detection Image">
                    </div>
                </div>

                <h2 class="subheader">Future Enhancement</h2>

                <ol>
                    <li>
                        <p class="highlight">Telemedicine and Remote Monitoring:</p>
                        <p>Expand the platform to support telemedicine consultations with veterinarians, allowing users to connect with veterinary professionals remotely for advice, diagnosis, and treatment planning. Additionally, integrate IoT (Internet of Things) devices for remote monitoring of animal vital signs and health parameters, providing real-time insights to caregivers and veterinarians.</p>
                    </li>
                    <li>
                        <p class="highlight">Community-driven Data Collection and Analysis:</p>
                        <p>Implement features that allow users to contribute anonymized data about their animals' health conditions and treatments. Aggregate this data to identify trends, emerging diseases, and regional health disparities, enabling proactive public health interventions and targeted veterinary services.</p>
                    </li>
                    <li>
                        <p class="highlight">Fundraising and Revenue Generation:</p>
                        <p>Explore revenue generation strategies such as subscription models offering tiered access to premium features, partnerships with pet healthcare companies, and sponsored content.</p>
                    </li>
                </ol>

                <h2 class="subheader">Contact Us</h2>

                <p>For any inquiries or suggestions, feel free to reach out to us at <a href="mailto:contact@email.com">contact@email.com</a>. We value your feedback and strive to continuously improve PetCareMate to better serve the pet care community.</p>
            """

            st.write(html_content, unsafe_allow_html=True)

    class GeminiHealthApp:
        def __init__(self):
            load_dotenv()  ## load all the environment variables
            self.api_key = os.getenv("GOOGLE_API_KEY")
            genai.configure(api_key=self.api_key)
            self.input_prompt = """ As a pet healthcare expert, your role is to identify symptoms of pet diseases from provided descriptions or images. You should then provide detailed information on the disease, including its causes, symptoms, prevention measures, and recommended medications if necessary.
                                    Your response should follow this format:
                                    1. **Disease Name:**
                                       - **Symptoms:** Brief explanation of common symptoms.
                                       - **Causes:** Overview of possible causes.
                                       - **Prevention Measures:** Recommendations to prevent the disease.
                                       - **Recommended Medications:** If applicable, suggest appropriate medications.

                                    Please ensure your responses are comprehensive and aimed at helping pet owners understand and manage their pet's health effectively. Remember to include a disclaimer at the end of your response stating that you are not a veterinarian, and encourage users to seek professional advice.
                                    """

        def get_gemini_response(self, input_text, image, prompt):
            model = genai.GenerativeModel('gemini-pro-vision')
            response = model.generate_content([input_text, image[0], prompt])
            return response.text

        def input_image_setup(self, uploaded_file):
            if uploaded_file is not None:
                bytes_data = uploaded_file.getvalue()

                image_parts = [
                    {
                        "mime_type": uploaded_file.type,
                        "data": bytes_data
                    }
                ]
                return image_parts
            else:
                raise FileNotFoundError("No file uploaded")

        def run(self):
            st.set_page_config(page_title="Gemini Health App")
            st.header("Gemini Health App")
            input_text = st.text_input("Input Prompt: ", key="input")
            uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
            image = ""
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image.", use_column_width=True)

            submit = st.button("Tell me the total calories")

            if submit:
                image_data = self.input_image_setup(uploaded_file)
                response = self.get_gemini_response(self.input_prompt, image_data, input_text)
                st.subheader("The Response is")
                st.write(response)

    class HealthManagementApp:
        def __init__(self):
            load_dotenv()  ## load all the environment variables
            self.api_key = os.getenv("GOOGLE_API_KEY")
            genai.configure(api_key=self.api_key)
            self.input_prompt = """
            You are an expert in pet healthcare where you need to identify the symptoms of pet diseases from the provided description or image and provide detailed information on the disease, its causes, prevention measures, and recommend appropriate medications if necessary.

            Your response should be in the following format:

            1. Disease Name:
               - Symptoms:
               - Causes:
               - Prevention Measures:
               - Recommended Medications (if applicable):


            Please provide comprehensive information to assist pet owners in understanding and managing their pet's health 
            effectively, you should not be allowed to answer other than pet care topics, and you should mention a disclaimer at the end of the answers/context that you are not an expert. Please ensure to connect with a veterinarian.
            """

        def get_gemini_response(self, input_text, image, prompt):
            model = genai.GenerativeModel('gemini-pro-vision')
            response = model.generate_content([input_text, image[0], prompt])
            return response.text

        def input_image_setup(self, uploaded_file):
            if uploaded_file is not None:
                bytes_data = uploaded_file.getvalue()

                image_parts = [
                    {
                        "mime_type": uploaded_file.type,
                        "data": bytes_data
                    }
                ]
                return image_parts
            else:
                raise FileNotFoundError("No file uploaded")

        def app(self):
            st.header("Gemini Health App")
            input_text = st.text_input("Input Prompt: ", key="input")
            uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
            image = ""
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image.", use_column_width=True)

            submit = st.button("Detect disease")

            if submit:
                image_data = self.input_image_setup(uploaded_file)
                response = self.get_gemini_response(self.input_prompt, image_data, input_text)
                st.subheader("Detected disease is")
                st.write(response)

    class ContactUs:
        @staticmethod
        def app():
            html_content = """
                <section class="contact_section layout_padding-top">
                  <div class="container-fluid">
                    <div class="row">
                      <div class="col-md-5 offset-md-1">
                        <div class="form_container">
                          <div class="heading_container">
                            <img src="images/heading-img.png" alt="">
                            <h2>
                              Request A Call Back
                            </h2>
                            <p>
                              It is a long established fact that a reader will be distracted by the
                            </p>
                          </div>
                          <form action="">
                            <div>
                              <input type="text" placeholder="Full Name " />
                            </div>
                            <div>
                              <input type="text" placeholder="Phone number" />
                            </div>
                            <div>
                              <input type="email" placeholder="Email" />
                            </div>
                            <div>
                              <input type="text" class="message-box" placeholder="Message" />
                            </div>
                            <div class="d-flex ">
                              <button>
                                SEND
                              </button>
                            </div>
                          </form>
                        </div>
                      </div>
                      <div class="col-md-6 px-0">
                        <div class="map_container">
                          <div class="map-responsive">
                            <iframe src="https://www.google.com/maps/embed/v1/place?key=AIzaSyA0s1a7phLN0iaD6-UE7m4qP-z21pH0eSc&q=Eiffel+Tower+Paris+France" width="600" height="300" frameborder="0" style="border:0; width: 100%; height:100%" allowfullscreen></iframe>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </section>
            """

            st.write(html_content, unsafe_allow_html=True)

    class statistics:
        @staticmethod
        def app():
            st.write('statistics')

    class MultiApp:
        def __init__(self):
            self.apps = []

        def add_app(self, title, func):
            self.apps.append({
                "title": title,
                "function": func
            })

    def run():
        multi_app = MultiApp()

        # Add existing apps
        multi_app.add_app("Home", AHome.app)
        multi_app.add_app("About us", AboutUs.app)
        multi_app.add_app("Contact us", ContactUs.app)
        multi_app.add_app("📊Stats", statistics.app)

        # Add Health Management App
        health_app = HealthManagementApp()
        multi_app.add_app("Detect disease", health_app.app)  # Use "Health Management" as the title

        with st.sidebar:
            app = option_menu(
                menu_title='PetCareMate',
                options=['Home', 'About us', 'Contact us', '📊Stats', 'Detect disease'],  # Use 'Health Management' here
                icons=['house-fill', 'person', 'phone', '', 'person-circle', 'heart'],
                menu_icon='chat-text-fill',
                default_index=1,
                styles={
                    "container": {"padding": "5!important", "background-color": 'black'},
                    "icon": {"color": "white", "font-size": "23px"},
                    "nav-link": {"color": "white", "font-size": "20px", "text-align": "left", "margin": "0px",
                                 "--hover-color": "#52c4f2"},
                    "nav-link-selected": {"background-color": "#02A6E8 "},
                }
            )

        for item in multi_app.apps:
            if app == item["title"]:
                item["function"]()

    run()


if __name__ == "__main__":
    main()


