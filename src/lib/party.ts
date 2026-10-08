


export type Party = "Democrat" | "Republican" | "Other"

export const PARTIES: Party[] = ["Democrat", "Republican", "Other"];


export const partyShortNames: Record<Party, string> = {
  Democrat: 'D',
  Republican: 'R',
  Other: '3P',
}

export const partyColors: Record<string, string> = {
  Democrat: '#3d66cd',
  Republican: '#cd3d3d',
  Other: '#6c757d',
  Unknown: '#adb5bd',
}