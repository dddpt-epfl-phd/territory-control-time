

const controlsTypes = [
    {
        //common to all:
        id: "<id>",
        start: "date-object",
        end: "date-object",
        tags: [],
        description: "",
        sources: ["source-objects","..."]
    },
    {
        type: "directControl",
        ruler: "<political-entity-id>",
        rulerTitle: "",
        ruled: "<political-entity-id>",
        // commons...
    },
    {
        type: "unknownControl",
        ruler: null,
        // commons...
    },
    {
        type: "sharedControl",
        rulers: [
            ["ruler-title/role","<political-entity-id>"]
            ,"..."
        ],
         // mainRuler to distinguish the main ruler if there is one?
        "mainRuler?": "<political-entity-id> or null",
        // commons...
    },
    {
        type: "contestedControl",
        rulers: [
            ["ruler-title/role","<political-entity-id>"]
            ,"..."
        ],
        // commons...
    },
    {
        type: "uncertainOneOfControl",
        possibilities: ["control-objects-without-dates", "..."],
        rulerBestGuess: ["<control-id>"]
        // commons...
    },
]

const datesTypes=[
    {
        type:"exactDate",
        date:"date" //accepted: YYYY, YYYY.MM, YYYY.MM.DD
    },
    {
        type:"uncertainAroundDate",
        date:"date", //accepted: YYYY, YYYY.MM, YYYY.MM.DD
        uncertainty: "duration" //accepted: nbY, nbM, nbD
    },
    {
        type: "uncertainBoundedDate",
        earliest: "date or null",
        latest: "date or null",
        bestGuess: "date or null"
    },
    {
        type: "uncertainPossibilitiesDate",
        possibilities: ["dates", "..."],
        bestGuess: "date"
    },
    {
        type: "unknownDate",
        bestGuess: "date"
    },
]

const politicalEntitiesTypes = [
    {
        //common to all:
        id: "<id>",
        name: "name",
        start: "date-object",
        end: "date-object",
        tags: [],
        description: "",
        sources: ["source-objects","..."]
    },
    {
        type: "politicalEntity",
        category: "territoire/ville/duché/comté/seigneurie etc..."
    },
    {
        type: "individual"
    },
    {
        type: "humanGroup",
        category: "dynastie/bourgeois/artisans/paysans etc...",
        members: ["individuals-ids", "..."]
    }
]

const sourcesTypes = [
    {url:""},
    {reference:""},
]