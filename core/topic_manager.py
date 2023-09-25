"""
    Topic manager
"""

# pylint: disable=C0301,C0103,C0304,C0303,W0611,W0511,R0913,R0402

from dataclasses import dataclass

@dataclass
class TopicItem:
    """Topic item"""
    name : str
    similarity_request : str
    similarity_threshold : float

    def __repr__(self):
        return self.name

class TopicManager():
    """Topic manager"""

    def get_topic_list(self) -> list[TopicItem]:
        """Return topic list"""
        return [
            TopicItem("Company overview", "Information about company", 0.5),
            TopicItem("Revenue breakdown", "", 0.5),
            TopicItem("Brand overviews", "Name of brends", 0.5),
            TopicItem("Competitive landscape", "", 0.5)
        ]