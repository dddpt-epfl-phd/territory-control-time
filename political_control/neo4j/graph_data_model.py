from abc import abstractmethod
from collections.abc import Iterable
import json
from os import read, stat
import re
from warnings import warn

from py2neo import Node, Relationship
from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom, Label


def short_dhsId(dhsId):
    return re.sub("dhs-","", dhsId)
def format_dhsId(dhsId):
    return "dhs-"+short_dhsId(dhsId)


# Dates
#######################################################

class HistoricalDate(GraphObject):
    
    historical_date=Label()

    readableId=Property()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.historical_date=True

    """ @property
    def readable_id(self):
        return self.readableId
    @readable_id.setter
    def readable_id(self, readable_id):
        self.readableId = readable_id
    @readable_id.deleter
    def readable_id(self):
        del self.readableId """

    @abstractmethod
    def is_in_interval(self, start, end, certain=False, whole_interval=False):
        raise Exception("HistoricalDate.is_in_interval() must be implemented in subclass",self.__class__)

    @staticmethod
    def parse_json(d, graph=None):
        if isinstance(d, str):
            return HistoricalDate.from_readable_id(d, graph)
        if "type" not in d:
            raise Exception("HistoricalDate.parse_json() date missing type:"+json.dumps(d))
        date = None
        if d["type"]=="KnownDate":
            if d["date"]:
                date = KnownDate._parse_json(d, graph=None)
            else:
                return None
        elif d["type"]=="UncertainAroundDate":
            date = UncertainAroundDate._parse_json(d, graph)
        elif d["type"]=="UncertainBoundedDate":
            date = UncertainBoundedDate._parse_json(d, graph)
        elif d["type"]=="UncertainPossibilitiesDate":
            date = UncertainPossibilitiesDate._parse_json(d, graph)
        else:
            raise Exception("HistoricalDate.parse_json() not valid"+ json.dumps(d))

        if "readableId" in d:
            date.readableId=d["readableId"]
        return date

    @staticmethod
    def from_readable_id(readableId, graph=None, strict_match=True):
        date=None
        if not strict_match:
            ".*"+readableId+".*"
        if graph:
            date = HistoricalDate.match(graph).where("_.readableId=~'"+readableId+"'")
        if not date:
            if graph:
                warn("Date.from_readable_id(): no matching date found for date readableId: "+readableId)
            else:
                warn("Date.from_readable_id(): no graph, creating empty HDate for date readableId: "+readableId)
                date = HistoricalDate()
                date.readableId=readableId
                return date
        if len(date)>1:
            warn("Date.from_readable_id(): multiple matches for readableId: "+readableId)
            return list(date)
        return date.first()

class KnownDate(HistoricalDate):
    date=Property()

    @staticmethod
    def _parse_json(d, graph=None):
        date = KnownDate()
        date.date=d["date"]
        return date

    @staticmethod
    def new(readable_id, date):
        d = KnownDate()
        d.readableId=readable_id
        d.date=date
        return d
        


class UncertainAroundDate(HistoricalDate):
    date=Property()
    uncertainty=Property()

    def _parse_json(d, graph=None):
        date = UncertainAroundDate()
        date.date=d["date"]
        date.uncertainty=d["uncertainty"]
        return date

    @staticmethod
    def new(readable_id, date, uncertainty):
        d = UncertainAroundDate()
        d.readableId=readable_id
        d.date=date
        d.uncertainty=uncertainty
        return d


class UncertainBoundedDate(HistoricalDate):
    earliest=Property()
    latest=Property()

    def _parse_json(d, graph=None):
        date = UncertainBoundedDate()
        if "earliest" in d:
            date.earliest=d["earliest"]
        if "latest" in d:
            date.latest=d["latest"]
        if "bestGuess" in d:
            date.bestGuess=d["bestGuess"]
        return date

    @staticmethod
    def new(readable_id, earliest=None, latest=None, best_guess=None):
        d = UncertainBoundedDate()
        d.readableId=readable_id
        d.earliest=earliest
        d.latest=latest
        d.bestGuess=best_guess
        return d


class UncertainPossibilitiesDate(HistoricalDate):
    possibilities=RelatedTo("HistoricalDate", "HAS_POSSIBILITY")

    def _parse_json(d, graph=None):
        date = UncertainPossibilitiesDate()
        for p in d["possibilities"]:
            date.possibilities.add(HistoricalDate.parse_json(p, graph))
        if "bestGuess" in d:
            date.bestGuess=d["bestGuess"]
        return date

    @staticmethod
    def new(readable_id, possibilities):
        d = UncertainPossibilitiesDate()
        d.readableId=readable_id
        for p in possibilities:
            d.possibilities.add(d)
        return d


"""
Comparing dates
=============================

Possible dates:
- known Y
- known YM
- known YMD
- UncertainBounded Earliest
- UncertainBounded Latest
- UncertainAround
- UncertainPossibilities
    -> take bestGuess

known Y, YM, YMD, suppose known dates with same Y:
 kY<kYMD or kY>kYMD are always true
 kY==kYMD is always false

certainifying comparison of uncertainBoundedDates:
ubd1 < ubd2:
    compare in order, with first defined positive result:
    ubd1.latest   < ubd2.earliest   ||
    ubd1.earliest < ubd2.earliest   ||
    ubd1.latest   < ubd2.latest     ||
    ubd1.earliest < ubd2.earliest   ||


proposition:
- default __lt__() __gt__() override with certainifying reasoning
- probabilistic comparison method for probabilistic comparison, assuming
    - normal distrib for uncertainAround
    - uniform distrib for UncertainBounded and UncertainPOssibilities
- uncertain comparison method (true, false, None) when not sure


"""

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

    start=RelatedTo("HistoricalDate", "START")
    end=RelatedTo("HistoricalDate", "END")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.historical_entity=True


# Political entities
#######################################################


class PoliticalEntity(HistoricalEntity):
    dhsId=Property()
    political_entity=Label()

    name=Property()
    category=Property()
    description=Property()

    sources=RelatedTo("Source", "HAS_SOURCE")

    controlling=RelatedTo("PoliticalControl", "HAS_CONTROL")
    controlled_by=RelatedFrom("PoliticalControl", "CONTROL_OVER")

    predecessors=RelatedTo("PoliticalEntity", "SUCCESSOR_OF")
    successors=RelatedFrom("PoliticalEntity", "SUCCESSOR_OF")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.political_entity=True


    """ @property
    def dhs_id(self):
        return self.dhsId
    @dhs_id.setter
    def dhs_id(self, dhs_id):
        self.dhsId = dhs_id
    @dhs_id.deleter
    def dhs_id(self):
        del self.dhsId """

    def set_first_mention(self, first_mention):
        for s in self.start:
            self.start.remove(s)
        new_start=UncertainBoundedDate(
            "first-mention-"+self.name.lower().replace(" ", "-"),
            latest=first_mention,
            best_guess=first_mention
        )
        self.start.add(new_start)
        return new_start

    @staticmethod
    def parse_json(pe, graph=None, DHS_sourced = False):
        if isinstance(pe, str):
            return HistoricalDate.from_readable_id(pe)
        if "type" not in pe:
            raise Exception("PoliticalEntity.parse_json() missing type:"+json.dumps(pe))
        political_entity = None
        if pe["type"]=="Territory":
            political_entity = Territory._parse_json(pe, graph)
        elif pe["type"]=="HumanGroup":
            political_entity = HumanGroup._parse_json(pe, graph)
        elif pe["type"]=="Individual":
            political_entity = Individual._parse_json(pe, graph)
        else:
            political_entity = PoliticalEntity()
        if "dhsId" in pe:
            political_entity.dhsId=pe["dhsId"]
        political_entity.name = pe["name"]
        political_entity.category= pe["category"]
        if "start" in pe:
            political_entity.start.add(HistoricalDate.parse_json(pe["start"], graph))
        if "end" in pe:
            political_entity.end.add(HistoricalDate.parse_json(pe["end"], graph))
        for s in pe["sources"]:
            political_entity.sources.add(Source.parse_json(s, graph))
        political_entity.DHS_sourced = DHS_sourced
        return political_entity

    @staticmethod
    def from_dhsId(graph, dhsId, more_than_one_expected = False, strict_match=False):
        if not strict_match:
            dhsId+=".*"
        gpes = [gpe for gpe in 
            PoliticalEntity.match(graph).where(r"_.dhsId=~'(dhs-)?"+dhsId+"'")
        ]
        if len(gpes)>1 and not more_than_one_expected:
            warn("PoliticalEntity.from_dhsId() more than 1 political entity")
        return gpes
    
    @staticmethod
    def from_name(graph, name_regex, strict_match=False):
        if not strict_match:
            name_regex=".*"+name_regex+".*"
        return [go for go in PoliticalEntity.match(graph).where(r"_.name=~'"+name_regex+r"'")]
    
    @staticmethod
    def dhsIds_from_name(graph, name_regex, strict_match=False):
        matches = PoliticalEntity.from_name(graph, name_regex, strict_match)
        return [(go.dhsId,go.name) for go in matches]

    @staticmethod
    def new(name, category, start, end, sources, predecessors=[],
            dhsId=None, description=None):
        pe = PoliticalEntity()
        pe.name=name
        pe.category=category
        pe.start.add(start)
        pe.end.add(end)
        if dhsId:
            pe.dhsId=dhsId
        if description:
            pe.description=description

        if not isinstance(sources, Iterable):
            sources=[sources]
        for s in sources:
            pe.sources.add(s)

        if not isinstance(predecessors, Iterable):
            predecessors=[predecessors]
        for p in predecessors:
            pe.predecessors.add(p)
            
        return pe


class Territory(PoliticalEntity):
    geometry_id=Property()

    @staticmethod
    def _parse_json(t, graph=None):
        territory = Territory()
        if "geometryId" in t:
            territory.geometry_id = t["geometryId"]
        return territory

class Individual(PoliticalEntity):
    @staticmethod
    def _parse_json(t, graph=None):
        pass

class HumanGroup(PoliticalEntity):
    members=RelatedFrom("Individual", "IS_MEMBER")

    @staticmethod
    def _parse_json(t, graph=None):
        pass

# Control
#######################################################
# (nodes because dates!)

class PoliticalControl(HistoricalEntity):
    political_control=Label()

    main_controller=RelatedFrom("PoliticalEntity", "IS_MAIN_CONTROLLER")
    controlled=RelatedTo("PoliticalEntity", "CONTROL_OVER")

    sources=RelatedTo("Source", "HAS_SOURCE")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.political_control=True

    @staticmethod
    def parse_json(pc, graph=None, DHS_sourced = False):
        if "type" not in pc:
            raise Exception("PoliticalControl.parse_json() missing type:"+json.dumps(pc))

        political_control = None
        if pc["type"]=="DirectControl":
            political_control = DirectControl._parse_json(pc, graph)
        elif pc["type"]=="UnknownControl":
            political_control = UnknownControl._parse_json(pc, graph)
        elif pc["type"]=="SharedControl":
            political_control = SharedControl._parse_json(pc, graph)
        elif pc["type"]=="ContestedControl":
            political_control = ContestedControl._parse_json(pc, graph)
        elif pc["type"]=="UncertainOneOfControl":
            political_control = UncertainOneOfControl._parse_json(pc, graph)
        else:
            raise Exception("PoliticalControl.parse_json() unknown type:"+json.dumps(pc))

        if "start" in pc:
            political_control.start.add(HistoricalDate.parse_json(pc["start"], graph))
        if "end" in pc:
            political_control.start.add(HistoricalDate.parse_json(pc["end"], graph))
        for s in pc["sources"]:
            political_control.sources.add(Source.parse_json(s, graph))
        political_control.DHS_sourced = DHS_sourced
        return political_control

    @staticmethod
    def _new(political_control_object, main_controller, controlled, start, end, sources):
        political_control_object.main_controller.add(main_controller)
        if not isinstance(controlled, Iterable):
            controlled=[controlled]
        for c in controlled:
            political_control_object.controlled.add(c)
        political_control_object.start.add(start)
        political_control_object.end.add(end)
        if not isinstance(sources, Iterable):
            sources=[sources]
        for s in sources:
            political_control_object.sources.add(s)
        return political_control_object

    @staticmethod
    def new(main_controller, controlled, start, end, sources):
        return PoliticalControl._new(PoliticalControl(), main_controller, controlled, start, end, sources)

class DirectControl(PoliticalControl):
    @staticmethod
    def _parse_json(t, graph=None):
        control = DirectControl()
        return control

    @staticmethod
    def new(main_controller, controlled, start, end, sources):
        return PoliticalControl._new(DirectControl(), main_controller, controlled, start, end, sources)

class UnknownControl(PoliticalControl):
    @staticmethod
    def _parse_json(t, graph=None):
        control = UnknownControl()
        return control

    @staticmethod
    def new(main_controller, controlled, start, end, sources):
        return PoliticalControl._new(UnknownControl(), main_controller, controlled, start, end, sources)

class MultiControl(PoliticalControl):
    controllers=RelatedFrom("PoliticalEntity", "IS_AMONG_CONTROLLERS")
    @staticmethod
    def _parse_json(t, graph=None):
        control = MultiControl()
        return control

    @staticmethod
    def _new(multi_control_object, main_controller, controllers, controlled, start, end, sources):
        pco =  PoliticalControl._new(multi_control_object, main_controller, controlled, start, end, sources)
        for c in controllers:
            pco.controllers.add(c)
        return pco

class SharedControl(MultiControl):
    @staticmethod
    def _parse_json(t, graph=None):
        control = SharedControl()
        return control

    @staticmethod
    def new(main_controller, controllers, controlled, start, end, sources):
        pco =  MultiControl._new(SharedControl(), main_controller, controllers, controlled, start, end, sources)
        return pco

class ContestedControl(MultiControl):
    @staticmethod
    def _parse_json(t, graph=None):
        control = ContestedControl()
        return control

    @staticmethod
    def new(main_controller, controllers, controlled, start, end, sources):
        pco =  MultiControl._new(ContestedControl(), main_controller, controllers, controlled, start, end, sources)
        return pco

class UncertainOneOfControl(MultiControl):
    @staticmethod
    def _parse_json(t, graph=None):
        control = UncertainOneOfControl()
        return control

    @staticmethod
    def new(main_controller, controllers, controlled, start, end, sources):
        pco =  MultiControl._new(UncertainOneOfControl(), main_controller, controllers, controlled, start, end, sources)
        return pco

# control relationships
# ------------------------

class HasControl(Relationship):
    pass

class ControlOver(Relationship):
    pass


# Bags
#######################################################

class BagControl:
    def __init__(self, start_date, main_controller, sources=[]):
        self.start_date = start_date
        self.main_controller = main_controller
        self.sources = sources
        if isinstance(sources, Iterable):
            self.sources=sources
        else:
            self.sources=[sources]

class BagDirectControl(BagControl):
    def __init__(self, start_date, main_controller, sources=[]):
        super().__init__(self, start_date, main_controller, sources)
    def to_control(self, controlled, end, sources):
        pass

class BagSharedControl(BagControl):
    def __init__(self, start_date, *controllers, sources=[]):
        super().__init__(self, start_date, controllers[0], sources)
        self.controllers = controllers
    def to_control(self, controlled, end, sources):
        pass
class BagContestedControl(BagControl):
    def __init__(self, start_date, *controllers, sources=[]):
        super().__init__(self, start_date, controllers[0], sources)
        self.controllers = controllers
    def to_control(self, controlled, end, sources):
        pass

class BaggedPolityJoining:
    def __init__(self, start, polity, sources=[]):
        self.polity=polity
        self.sources=sources
        self.start=start 
class BaggedPolityLeaving:
    def __init__(self, move_date, polity, sources=[]):
        self.polity=polity
        self.sources=sources
        self.move_date=move_date 

class PolityBag:
    """
    PolityBag: representing loose group of Polities
    
    The aim of the polity bag is to avoid multiple entry of the same
    info and so reduce errors. 
    """
    def __init__(self, name, end_date, *date_controller_source_list , sources=[]):
        """
        PolityBag constructor

        Arguments:
        name -- informal name 
        end_date -- the end date of the last control relationship
        date_controller_source_list -- see below for description of a single date_controller_source
        sources -- array of Sources that will be shared by all control relationships implied by this PolityBag

        date_controller_source is a tuple of length 2 or 3 with in order:
        1) a Date object, the start date of the control for those controller(s)
        2) a controller, see below
        3) optional, a Source or list of Sources documenting control of the controller

        controller must be one of:
        - a single polity, implying DirectControl from given Polity
        - a list of polities, implying SharedControl and main_controller is the first in the list
        - any BagXXControl object, in most cases a BagContestedControl for contested control

        """
        self.name=name
        self.end_date=end_date

        self.bag_controls = []
        for dcs in date_controller_source_list:
            if len(dcs)>3 or len(dcs)<1:
                raise Exception("PolityBag.__init__(): PolityBag '"+name+"', date_controller_source not of length 3: "+str(dcs))
            
            sources= sources=dcs[2] if len(dcs)>=3 else []                

            if isinstance(dcs[1], BagControl):
                self.bag_controls.append(dcs[1])
            if isinstance(dcs[1], PoliticalEntity):
                self.bag_controls.append(BagDirectControl(dcs[0], dcs[1], sources))
            if isinstance(dcs[1], Iterable):
                self.bag_controls.append(BagSharedControl(dcs[0], *dcs[1], sources=sources))    
        
        self.all_sources = sources
        self.bagged_polities_joining = []
        self.bagged_polities_leaving = []


    def add(self, start_date, *joining_polities, sources=[]):
        """
        Add one or more polity to the polity bag

        end_date should only be specified if it's not moving to another bag.
        If it's moving to another bag, use move_to
        """
        for polity in joining_polities:
            self.bagged_polities_joining.append(BaggedPolityJoining(start_date, polity, sources))

    def move_to(self, date, destination_bag, *leaving_polities, sources=[]):
        """
        Move one or more polities to another polity bag on given date
        also calls destination_bag.add(...)

        If a leaving polity is not already in this bag, raises an exception.
        TODO: check dates and if not already leaving
        """
        for polity in leaving_polities:
            if len([bp.polity for bp in self.bagged_polities_joining if bp.polity==polity])==0:
                raise Exception("PolityBage.move_to(): moving polity '"+polity.name+"' that isn't in the polity bag")
            self.bagged_polities_leaving.append(BaggedPolityLeaving(date, polity, sources))
        destination_bag.add(date, *leaving_polities, sources=sources)
        
    def merge(self, other_bag, merge_date, sources):
        """Create a new PolityBag consisting of the 2 merged polityBags on given date"""
        pass
    def to_control_relationships(self):
        """
        Assumption:
        - controllers are already ordered from first to last controller temporally
        - for each controlled entity, its joining & leaving are ordered temporally and dates are consistent

        Algorithm:
        - iterate over 
        """
        pass

# Sources & references
#######################################################

class Source(GraphObject):
    source=Label()

    description=Property()
    author=Property()

    sourcing=RelatedFrom("HAS_SOURCE")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source=True

    @staticmethod
    def parse_json(s, graph=None):
        if "url" in s:
            if "hls-dhs-dss.ch" in s["url"]:
                return DHSArticle.parse_json(s, graph)
            else:
                return URLSource.parse_json(s, graph)
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
    def parse_json(us, graph=None):
        if "url" not in us:
            raise Exception("URLSource.parse_json() no url in source "+json.dumps(us))
        url_source = URLSource()
        url_source.url=us["url"]
        return url_source


dhs_article_id_regex = re.compile(r"articles/(.+?)/")
class DHSArticle(URLSource):
    __primarykey__="dhsId"
    dhsId=Property()

    tags = RelatedTo("DHSTag", "HAS_DHS_TAG")

    """ @property
    def dhs_id(self):
        return self.dhsId
    @dhs_id.setter
    def dhs_id(self, dhs_id):
        self.dhsId = dhs_id
    @dhs_id.deleter
    def dhs_id(self):
        del self.dhsId """

    @staticmethod
    def parse_json(dhsa, graph=None):
        if "url" not in dhsa:
            raise Exception("DHSArticle.parse_json() no url in source "+json.dumps(dhsa))
        if "hls-dhs-dss.ch" not in dhsa["url"]:
            raise Exception("DHSArticle.parse_json() no url in source "+json.dumps(dhsa))
        article = DHSArticle()
        article.url=dhsa["url"]

        article_id_match = dhs_article_id_regex.search(dhsa["url"])
        if article_id_match:
            article.dhsId = "dhs-"+article_id_match.group(1)
        
        if "tags" in dhsa:
            for tag in dhsa["tags"]:
                article.tags.add(DHSTag.parse_json(tag, graph))
        return article

    @staticmethod
    def from_dhsId(graph, dhsId):
        return DHSArticle.match(graph).where(r"_.dhsId=~'(dhs-)?"+dhsId+"'").first()

    @staticmethod
    def scrape_from_dhs(dhsId):
        import requests as r
        from lxml import html

        real_dhsId = re.sub("dhs-","", dhsId)
        url = "https://hls-dhs-dss.ch/fr/articles/"+real_dhsId
        page = r.get(url)
        pagetree = html.fromstring(page.content)
        tags = [{"tag":el.text_content(),"url":el.xpath("@href")[0]} for el in pagetree.cssselect(".hls-service-box-right a")]
        
        article = DHSArticle()
        article.dhsId="dhs-"+real_dhsId
        article.url="dhs-"+url
        for t in tags:
            tag = DHSTag()
            tag.tag=str(t["tag"])
            tag.url=str(t["url"])
            article.tags.add(tag)
        return article

class DHSTag(GraphObject):
    __primarykey__="tag"
    tag=Property()
    url=Property()

    tagging = RelatedFrom("DHSArticle", "HAS_DHS_TAG")

    @staticmethod
    def parse_json(dt, graph=None):
        tag = DHSTag()
        tag.url=dt["url"]
        tag.tag=dt["tag"]
        return tag


