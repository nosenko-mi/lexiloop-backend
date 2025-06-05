from pattern.text import (
    INFINITIVE, PRESENT, PAST, FUTURE,  # tense
    FIRST, SECOND, THIRD,  # person
    SINGULAR, PLURAL, SG, PL,  # number
    PROGRESSIVE, PERFECTIVE, PARTICIPLE, GERUND,  # aspect
    INDICATIVE,  # mood
)
from pattern.text.en import conjugate, lemma, lexeme


tag_to_verb_map = {
    "VB": {"tense": INFINITIVE},  # verb, base form
    "VBD": {"tense": PAST},  # verb, past tense
    "VBG": {"aspect": GERUND},  # verb, present participle or gerund
    "VBN": {"tense": PAST, "aspect": PARTICIPLE},  # verb, past participle
    # verb, present tense, not 3rd person singular
    "VBP": {"tense": PRESENT, "number": SG, "person": 1},
    # verb, present tense, 3rd person singular
    "VBZ": {"tense": PRESENT, "number": SG, "person": 3},

    "VBDN": {"tense": PAST, "negated": True},  # verb, past tense
    # verb, present tense, not 3rd person singular
    "VBPN": {"tense": PRESENT, "number": SG, "person": 1, "negated": True},
    # verb, present tense, 3rd person singular
    "VBZN": {"tense": PRESENT, "number": SG, "person": 3, "negated": True},
}

negative_tags = [("not", "RB"), ("n't", "RB")]

verb_tags = ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "VBDN", "VBPN", "VBZN",]


def check_negative(target_idx: int, tags: list[tuple]) -> bool:
    __pattern_stopiteration_workaround()

    if target_idx == (len(tags)-1):
        return False

    return tags[target_idx+1] == negative_tags[0] or tags[target_idx+1] == negative_tags[1]


def convert_verb_to_negative(target_idx: int, tags: list[tuple]) -> tuple:
    __pattern_stopiteration_workaround()

    new_tag = tags[target_idx][1] + "N"
    new_verb = tags[target_idx][0]

    if tags[target_idx + 1] == negative_tags[0]:
        new_verb = new_verb + " " + negative_tags[0][0]
    elif tags[target_idx + 1] == negative_tags[1]:
        new_verb = new_verb + negative_tags[1][0]
    else:
        new_verb = new_verb + " " + negative_tags[0][0]

    new_tags = tags[:]
    new_tags.insert(target_idx, (new_verb, new_tag))
    new_tags.pop(target_idx+1)
    new_tags.pop(target_idx+1)

    negative_verb = (target_idx, (new_verb, new_tag))

    return (negative_verb, new_tags)


def generate_tenses_from_tags(tags: list[str], verb: str) -> list[str]:
    __pattern_stopiteration_workaround()

    result = []
    for tag in tags:
        is_equal, new_verb = generate_tense_from_tag(tag, verb)
        result.append(new_verb)

    return result


def generate_tense_from_tag(tag: str, verb: str) -> tuple[bool, str | None]:
    __pattern_stopiteration_workaround()

    new_verb = __map_to_tense(verb, tag)
    is_equal = verb == new_verb

    return (is_equal, new_verb)


def __map_to_tense(verb: str, tag: str) -> str | None:
    lem = lemma(verb)
    complete_verb = conjugate(lem, **tag_to_verb_map[tag])

    if complete_verb: 
        return complete_verb
    else:
        return None 


def __pattern_stopiteration_workaround():
    try:
        lexeme('gave')
    except:
        pass


# print (conjugate(verb='do', tense=INFINITIVE))
# print (conjugate(verb='do', tense=PRESENT, number=SG))
# print (conjugate(verb='do', tense=PRESENT, aspect = PROGRESSIVE))
# print (conjugate(verb='do', tense=PAST, number=SG, person=1))
# print (conjugate(verb='do', tense=PAST, aspect = PARTICIPLE))
# print (conjugate(verb='do', tense=PRESENT, number=SG, person=1, negated=True))
# print (conjugate(verb='do', tense=PRESENT, number=SG, person=3, negated=True))
# print (conjugate(verb='do', tense=PAST, number=SINGULAR, negated=True, mood=INDICATIVE ))
# print (conjugate(verb='do', tense=PAST, number=PLURAL, negated=True, ))
# print (conjugate(verb='be', tense=PAST, number=SG, negated=True, ))
# print (conjugate(verb='be', tense=PAST, number=PL, negated=True, ))
