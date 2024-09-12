from abc import ABC, abstractmethod


class model(ABC):

  @abstractmethod
  def predict(self, sentence):
      pass
