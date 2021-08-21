

const controlsTypess = [
    {
        type: "directControl",
        id: "",
        rulers: "",
        rulerTitle: "",
        ruled: "",
        start: {
            type:"exactDate",
            date:"" //accepted: YYYY, YYYY.MM, YYYY.MM.DD
        },
        end: {
            type:"exactDate",
            date:"" //accepted: YYYY, YYYY.MM, YYYY.MM.DD
        },
        tags: [],
        description: "",
        sources: []
    },
    {
        type: "unknownControl",
        ruler: null,
        id: "",
        start: {
            type:"exactDate",
            date:"" //accepted: YYYY, YYYY.MM, YYYY.MM.DD
        },
        end: {
            type:"exactDate",
            date:"" //accepted: YYYY, YYYY.MM, YYYY.MM.DD
        },
        tags: [],
        description: "",
        sources: []
    },
    {
        type: "sharedControl",
        rulers: [
            ["titleRole","peid"],
            ["titleRole","peid"],
        ],
        mainRuler: "",
        id: "",
        start: {
            type:"exactDate",
            date:"" //accepted: YYYY, YYYY.MM, YYYY.MM.DD
        },
        end: {
            type:"exactDate",
            date:"" //accepted: YYYY, YYYY.MM, YYYY.MM.DD
        },
        tags: [],
        description: "",
        sources: []
    },
    {
        type: "contestedControl",
        rulers: [
            ["titleRole","peid"],
            ["titleRole","peid"],
        ],
        id: "",
        start: {
            type:"exactDate",
            date:"" //accepted: YYYY, YYYY.MM, YYYY.MM.DD
        },
        end: {
            type:"exactDate",
            date:"" //accepted: YYYY, YYYY.MM, YYYY.MM.DD
        },
        tags: [],
        description: "",
        sources: []
    },
    {
        type: "uncertainOneOfControl",
        possibilities: [],
        rulerBestGuess: "",
        id: "",
        start: {
            type:"exactDate",
            date:"" //accepted: YYYY, YYYY.MM, YYYY.MM.DD
        },
        end: {
            type:"exactDate",
            date:"" //accepted: YYYY, YYYY.MM, YYYY.MM.DD
        },
        tags: [],
        description: "",
        sources: []
    },
]

const datesTypes=[
    {
        type:"exactDate",
        date:"" //accepted: YYYY, YYYY.MM, YYYY.MM.DD
    },
    {
        type:"uncertainAroundDate",
        date:"", //accepted: YYYY, YYYY.MM, YYYY.MM.DD
        uncertainty: "" //accepted: nbY, nbM, nbD
    },
    {
        type: "uncertainBoundedDate",
        earliest: "",
        latest: "",
        bestGuess: ""
    },
    {
        type: "uncertainPossibilitiesDate",
        possibilities: [],
        bestGuess: ""
    },
    {
        type: "unknownDate",
        bestGuess: ""
    },
]

const politicalEntitiesTypes = [
    {
        type: "politicalEntity",
        id: "",
        name: "",
        category: "",
        start: {
            type:"exactDate",
            date:"" //accepted: YYYY, YYYY.MM, YYYY.MM.DD
        },
        end: {
            type:"exactDate",
            date:"" //accepted: YYYY, YYYY.MM, YYYY.MM.DD
        },
        tags: [],
        description: "",
        sources: []
    },
    {
        type: "individual",
        id: "",
        name: "",
        birth: {
            type:"exactDate",
            date:"" //accepted: YYYY, YYYY.MM, YYYY.MM.DD
        },
        death: {
            type:"exactDate",
            date:"" //accepted: YYYY, YYYY.MM, YYYY.MM.DD
        },
        tags: [],
        description: "",
        sources: []
    },
    {
        type: "humanGroup",
        id: "",
        name: "",
        category: "",
        members: [],
        start: {
            type:"exactDate",
            date:"" //accepted: YYYY, YYYY.MM, YYYY.MM.DD
        },
        end: {
            type:"exactDate",
            date:"" //accepted: YYYY, YYYY.MM, YYYY.MM.DD
        },
        tags: [],
        description: "",
        sources: []
    }
]


const sourcesTypes = [
    {url:""},
    {reference:""},
]