import statesRaw from "../data/states.json"

export type StatePO = string

export type State = {
  statePO: StatePO
  stateName: string
}

export type StateEntry = State & {
  id: string
}

export const states = statesRaw as State[]
