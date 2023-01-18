from Question import Question

class Queue:
    def __init__(self):
        """Represents a queue of questions to be answered by ChatGPT
        """
        self.__queue = []

    def push(self, question: Question):
        """Adds a question to the queue

        Args:
            question (Question): The question to add to the queue

        Raises:
            TypeError: If the question is not of type Question
        """
        if not isinstance(question, Question):
            raise TypeError("Question must be of type Question")
        self.__queue.append(question)

    def pop(self) -> Question:
        """Removes the first question from the queue and returns it

        Returns:
            Question: The first question in the queue
        """
        return self.__queue.pop(0)

    def __len__(self) -> Question:
        return len(self.__queue)

    def __getitem__(self, index) -> Question:
        return self.__queue[index]

