from abc import abstractmethod
import json
import re

from py2neo import Node, Relationship
from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom, Label

# Dates
#######################################################

class HistoricalDate(GraphObject):
    historical_date=Label()

    readableId=Property()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.historical_date=True

    @abstractmethod
    def is_in_interval(self, start, end, certain=False, whole_interval=False):
        raise Exception("HistoricalDate.is_in_interval() must be implemented in subclass",self.__class__)

    @staticmethod
    def parse_json(d):
        if isinstance(d, str):
            return HistoricalDate.fromReadableId(d)
        if "type" not in d:
            raise Exception("HistoricalDate.parse_json() date missing type:"+json.dumps(d))
        date = None
        if d["type"]=="exactDate":
            if d["date"]:
                date = KnownDate._parse_json(d)
            else:
                return None
        elif d["type"]=="UncertainAroundDate":
            date = UncertainAroundDate._parse_json(d)
        elif d["type"]=="UncertainBoundedDate":
            date = UncertainBoundedDate._parse_json(d)
        elif d["type"]=="UncertainPossibilitiesDate":
            date = UncertainPossibilitiesDate._parse_json(d)
        else:
            raise Exception("HistoricalDate.parse_json() not valid"+ json.dumps(d))

        if "readableId" in d:
            date.readableId=d["readableId"]
        return date

    @staticmethod
    def fromReadableId(d):
        raise Exception("Date.fromReadableId() not implemented")

class KnownDate(HistoricalDate):
    date=Property()

    @staticmethod
    def _parse_json(d):
        date = KnownDate()
        date.date=d["date"]
        return date


class UncertainAroundDate(HistoricalDate):
    date=Property()
    uncertainty=Property()

    def _parse_json(d):
        date = UncertainAroundDate()
        date.date=d["date"]
        date.uncertainty=d["uncertainty"]
        return date


class UncertainBoundedDate(HistoricalDate):
    earliest=Property()
    latest=Property()

    def _parse_json(d):
        date = UncertainBoundedDate()
        if "earliest" in d:
            date.earliest=d["earliest"]
        if "latest" in d:
            date.latest=d["latest"]
        if "bestGuess" in d:
            date.bestGuess=d["bestGuess"]
        return date


class UncertainPossibilitiesDate(HistoricalDate):
    possibilities=RelatedTo("HAS_POSSIBILITY", "HistoricalDate")

    def _parse_json(d):
        date = UncertainPossibilitiesDate()
        for p in d["possibilities"]:
            date.possibilities.add(HistoricalDate.parse_json(p))
        if "bestGuess" in d:
            date.bestGuess=d["bestGuess"]
        return date


# date relationships
# ------------------------

class Start(Relationship):
    pass
class End(Relationship):
    pass

# HistoricalEntity Node
# ------------------------

class HistoricalEntity(GraphObject):
    historical_entity=Label()
    DHS_sourced=Label()

    start=RelatedTo("START", "HistoricalDate")
    end=RelatedTo("END", "HistoricalDate")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.historical_entity=True


# Political entities
#######################################################


class PoliticalEntity(HistoricalEntity):
    dhs_id=Property()
    political_entity=Label()

    name=Property()
    category=Property()
    description=Property()

    sources=RelatedTo("HAS_SOURCE", "Source")

    controlling=RelatedTo("HAS_CONTROL", "PoliticalControl")
    controlled_by=RelatedFrom("CONTROL_OVER", "PoliticalControl")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.political_entity=True

    @staticmethod
    def parse_json(pe, DHS_sourced = False):
        if isinstance(pe, str):
            return HistoricalDate.fromReadableId(pe)
        if "type" not in pe:
            raise Exception("PoliticalEntity.parse_json() missing type:"+json.dumps(pe))
        political_entity = None
        if pe["type"]=="Territory":
            political_entity = Territory._parse_json(pe)
        elif pe["type"]=="HumanGroup":
            political_entity = HumanGroup._parse_json(pe)
        elif pe["type"]=="Individual":
            political_entity = Individual._parse_json(pe)
        else:
            political_entity = PoliticalEntity()
        political_entity.dhs_id=pe["id"]
        political_entity.name = pe["name"]
        political_entity.category= pe["category"]
        if "start" in pe:
            political_entity.start.add(HistoricalDate.parse_json(pe["start"]))
        if "end" in pe:
            political_entity.start.add(HistoricalDate.parse_json(pe["end"]))
        for s in pe["sources"]:
            political_entity.sources.add(Source.parse_json(s))
        political_entity.DHS_sourced = DHS_sourced
        return political_entity

class Territory(PoliticalEntity):
    geometry_id=Property()

    @staticmethod
    def _parse_json(t):
        territory = Territory()
        if "geometryId" in t:
            territory.geometry_id = t["geometryId"]
        return territory

class Individual(PoliticalEntity):
    @staticmethod
    def _parse_json(t):
        pass

class HumanGroup(PoliticalEntity):
    members=RelatedFrom("IS_MEMBER", "Individual")

    @staticmethod
    def _parse_json(t):
        pass

# Control
#######################################################
# (nodes because dates!)

class PoliticalControl(HistoricalEntity):
    political_control=Label()

    controllers=RelatedFrom("HAS_CONTROL", "PoliticalEntity")
    controlled=RelatedTo("CONTROL_OVER", "PoliticalEntity")

    sources=RelatedTo("HAS_SOURCE", "Source")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.political_control=True

    @staticmethod
    def parse_json(pc, DHS_sourced = False):
        if "type" not in pc:
            raise Exception("PoliticalControl.parse_json() missing type:"+json.dumps(pc))f pe["type"]=="Territory":

        political_control = None
        if pc["type"]=="DirectControl":
            political_control = DirectControl._parse_json(pc)
        elif pc["type"]=="UnknownControl":
            political_control = UnknownControl._parse_json(pc)
        elif pc["type"]=="SharedControl":
            political_control = SharedControl._parse_json(pc)
        elif pc["type"]=="ContestedControl":
            political_control = ContestedControl._parse_json(pc)
        elif pc["type"]=="UncertainOneOfControl":
            political_control = UncertainOneOfControl._parse_json(pc)
        else:
            raise Exception("PoliticalControl.parse_json() unknown type:"+json.dumps(pc))f pe["type"]=="Territory":

        if "start" in pc:
            political_control.start.add(HistoricalDate.parse_json(pc["start"]))
        if "end" in pc:
            political_control.start.add(HistoricalDate.parse_json(pc["end"]))
        for s in pc["sources"]:
            political_control.sources.add(Source.parse_json(s))
        political_control.DHS_sourced = DHS_sourced
        return political_control

class DirectControl(PoliticalControl):
    @staticmethod
    def _parse_json(t):
        control = DirectControl()
        return control

class UnknownControl(PoliticalControl):
    @staticmethod
    def _parse_json(t):
        control = UnknownControl()
        return control

class SharedControl(PoliticalControl):
    main_controller=RelatedFrom("IS_MAIN_CONTROLLER", "PoliticalEntity")
    @staticmethod
    def _parse_json(t):
        control = SharedControl()
        return control

class ContestedControl(PoliticalControl):
    main_controller=RelatedFrom("IS_MAIN_CONTROLLER", "PoliticalEntity")
    @staticmethod
    def _parse_json(t):
        control = ContestedControl()
        return control

class UncertainOneOfControl(PoliticalControl):
    likeliest_controller=RelatedTo("HAS_POSSIBLE_CONTROL", "PoliticalControl")
    possible_controls=RelatedTo("IS_LIKELIEST_CONTROL", "PoliticalControl")
    @staticmethod
    def _parse_json(t):
        control = UncertainOneOfControl()
        return control

# control relationships
# ------------------------

class HasControl(Relationship):
    pass

class ControlOver(Relationship):
    pass


# Sources & references
#######################################################

class Source(Node):
    source=Label()

    description=Property()
    author=Property()

    sourcing=RelatedFrom("HAS_SOURCE")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source=True

    @staticmethod
    def parse_json(s):
        if "url" in s:
            if "hls-dhs-dss.ch" in s["url"]:
                return DHSArticle.parse_json(s)
            else:
                return URLSource.parse_json(s)
        else:
            raise Exception("Source.parse_json() no url in source "+json.dumps(s))


class Reference(Source):
    reference=Property()


class URLSource(Source):
    URL=Label(name="URL")
    url=Property()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.URL=True

    @staticmethod
    def parse_json(us):
        if "url" not in us:
            raise Exception("URLSource.parse_json() no url in source "+json.dumps(us))
        url_source = URLSource()
        url_source.url=us["url"]
        return url_source


dhs_article_id_regex = re.compile(r"articles/(.+?)/")
class DHSArticle(URLSource):
    __primarykey__="dhsId"
    dhs_id=Property()

    tags = RelatedFrom("DHS_TAG_OF","DHSTag")

    @staticmethod
    def parse_json(dhsa):
        if "url" not in dhsa:
            raise Exception("DHSArticle.parse_json() no url in source "+json.dumps(dhsa))
        if "hls-dhs-dss.ch" not in dhsa["url"]:
            raise Exception("DHSArticle.parse_json() no url in source "+json.dumps(dhsa))
        article = DHSArticle()
        article.url=dhsa["url"]

        article_id_match = dhs_article_id_regex.search(dhsa["url"])
        if article_id_match:
            article.dhs_id = "dhs-"+article_id_match.group(1)
        
        for tag in dhsa["tags"]:
            article.tags.add(DHSTag.parse_json(tag))
        return article


class DHSTag(GraphObject):
    __primarykey__="tag"
    tag=Property()
    url=Property()

    tagging = RelatedTo("DHS_TAG_OF","DHSArticle")

    @staticmethod
    def parse_json(dt):
        tag = DHSTag()
        tag.url=dt["url"]
        tag.tag=dt["tag"]


