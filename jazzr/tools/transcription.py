from music21 import stream, clef, tempo, meter, note, duration, metadata, tie, pitch
import math, os

ONSET = 0
TIE = 1

def save_pdf(S, annotation=None, filename='transcription', barlevel=0, quiet=True, pitches=None):
  score = transcribe(S, annotation=annotation, barlevel=barlevel, pitches=pitches)
  out = open('{0}.xml'.format(filename), 'w')
  out.write(score.musicxml)
  out.close()
  pipe = ''
  if quiet:
    pipe = '> /dev/null'
  os.system('musescore -o "{0}.pdf" "{0}".xml {1}'.format(filename, pipe))
  os.system('rm {0}.xml'.format(filename))

def save_midi(S, annotation=None, pitches=None, filename='transcription', barlevel=0, quiet=True):
  score = transcribe(S, annotation=annotation, barlevel=barlevel, pitches=pitches)
  out = open('{0}.xml'.format(filename), 'w')
  out.write(score.musicxml)
  out.close()
  pipe = ''
  if quiet:
    pipe = '> /dev/null'
  os.system('musescore -o "{0}.mid" "{0}".xml {1}'.format(filename, pipe))
  os.system('rm {0}.xml'.format(filename))

def view_pdf(S, annotation=None, pitches=None, barlevel=0, quiet=True):
  save_pdf(S, annotation=annotation, barlevel=barlevel, pitches=pitches)
  pipe = ''
  if quiet:
    pipe = '> /dev/null'
  os.system('evince transcription.pdf {0}'.format(pipe))
  os.system('rm transcription.pdf')

def save_xml(S, annotation=None, pitches=None, filename='transcription', barlevel=0, quiet=True):
  score = transcribe(S, annotation=annotation, barlevel=barlevel, pitches=pitches)
  out = open('{0}.xml'.format(filename), 'w')
  out.write(score.musicxml)
  out.close()

def musescore(S, annotation=None, pitches=None, filename='transcription', barlevel=0, quiet=True):
  save_xml(S, annotation=annotation, barlevel=barlevel, filename=filename, pitches=pitches)
  pipe = ''
  if quiet:
    pipe = '> /dev/null'
  os.system('musescore "{0}".xml'.format(filename, pipe))



def transcribe(S, pitches=None, annotation=None, barlevel=0):
  title = 'Transcription of rhythmic analysis'
  if annotation:
    title = annotation.name
  score = stream.Score()
  score.metadata = metadata.Metadata()
  score.metadata.title = title
  score.metadata.composer = ''
  part = stream.Part()
  part.insert(stream.Measure())
  part[0].insert(0, clef.TrebleClef())
  part[0].insert(0, meter.TimeSignature('4/4'))
  notelist = scorelist(S, barlevel=barlevel)
  lastmeasure = -1
  measure = 0
  position = 0
  notesInserted = False
  counter = 0
  for item in notelist:
    if measure > lastmeasure:
      part.append(stream.Measure())
      lastmeasure = measure
    if item[0] == ONSET:
      notesInserted = True
      n = note.Note(quarterLength=4*item[1])
      n.pitch = pitch.Pitch('F')
      if annotation:
        n.midi = annotation.pitch(item[2])
      elif pitches:
        n.midi = pitches[counter] 
        counter += 1
      part[measure].append(n)
    elif item[0] == TIE:
      if not notesInserted:
        part[measure].append(note.Rest(quarterLength=4*item[1]))
      else:
        n = note.Note(quarterLength=4*item[1])
        if len(part[measure]) > 0:
          part[measure][-1].tie = tie.Tie('start')
          n.pitch = part[measure][-1].pitch
        else:
          part[measure-1][-1].tie = tie.Tie('start')
          n.pitch = part[measure-1][-1].pitch
        n.tie = tie.Tie('end')
        part[measure].append(n)
    position += item[1]
    if position == 1:
      position = 0
      measure += 1
    if position > 1:
      position = 0
      measure += 1
      print 'Warning, items don\'t sum to one.'
  score.append(part)
  return score

def scorelist(S, barlevel=0, depth=0, duration=1):
  score = []
  if S.isOnset():
    score = [(ONSET, duration, S.index)]
  if S.isTie():
    score = [(TIE, duration, 0)]
  if S.isSymbol():
    if depth >= barlevel:
      duration /= float(len(S.children))
    for child in S.children:
      score += scorelist(child, depth=depth+1, barlevel=barlevel, duration=duration)
  return score

