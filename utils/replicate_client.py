import os
import replicate
from dotenv import load_dotenv

load_dotenv()
MODEL_ID = str(os.getenv("MODEL_ID"))

class ImageEvaluator:
    def __init__(self, model_id):
        self.model_id = model_id
        
    def evaluate_image(self, image_path):
        output = replicate.run(
            self.model_id,
            input={
                "image": open(image_path, "rb"),
                "task": "visual_question_answering",
                "question": "is this a face?"
            }
        )
        output = output.split()[-1]
        # Determine if output indicates image is a face
        return output.lower() == 'yes'
            
    def ask_question(self, image_path, question):
        output = replicate.run(
            self.model_id,
            input={
                "image": open(image_path, "rb"),
                "task": "visual_question_answering",
                "question": question
            }
        )
        output = output.split()[-1]
        return output.lower()

if __name__ == "__main__":
    evaluator = ImageEvaluator(MODEL_ID)
    is_face = evaluator.evaluate_image("test_image.png")
    print(f"Is a face? : {is_face}")
    response = evaluator.ask_question("test_image.png", "what is his hair color?")
    print(f"Response for question: {response}")
