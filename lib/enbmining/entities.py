import re
from pathlib import Path

from .nlp import WordTokenizer


class Entity:

    """Base class of an Entity (Party or Grouping)."""

    def __init__(self, name, canonical_name=None):
        """Initializes an entity with its name and a canonical_name.

        If the entity is an alias, the canonical name contains the name of the
        original entity."""
        self.name = name
        self.canonical_name = (
            canonical_name if canonical_name is not None else name
        )
        # Keep track of the NLTK multi-word expression token for mapping.
        tokenizer = WordTokenizer([name])
        self.token = tokenizer.tokenize(name)[0]

    def __repr__(self):
        return self.canonical_name

    def __str__(self):
        if self.name != self.canonical_name:
            return f'{self.name} [{self.canonical_name}]'
        else:
            return self.name

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.canonical_name == other.canonical_name
        )

    def __hash__(self):
        return hash((self.name, self.canonical_name))

    @classmethod
    def _parse(cls, path):
        path = Path(path)
        with path.open(encoding="utf8") as f:
            return [
                cls._parse_line(line.strip())
                for line in f.readlines()
                if line != ''
            ]

    @staticmethod
    def _parse_line(line):
        def get_entity(line):
            # Match the text before the colon...
            entity = re.match(r'(.*?)\s*?:', line)
            if entity is not None:
                return entity.group(1)
            # ...or the text until the open bracket...
            entity = re.match(r'(.*?)\s*?\[', line)
            if entity is not None:
                return entity.group(1)
            # ...or the whole line.
            return line

        def get_aliases(line):
            line = re.sub(r'\[.*\]', '', line)
            if ':' in line:
                _, aliases = line.split(':')
                delim = ';' if ';' in aliases else ','
                return {alias.strip() for alias in aliases.split(delim)}
            else:
                return set()

        def get_groupings(line):
            groupings = re.search(r'\[(.*)\]', line)
            if groupings is None:
                return set()
            return {g.strip() for g in groupings.group(1).split(',')}

        return get_entity(line), get_aliases(line), get_groupings(line)

    @classmethod
    def _combine(cls, entity, aliases):
        """Generates all combinations of names, aliases, and determinants."""
        # Add the base entity (it is the alias of no other entity).
        result = {cls(entity)}
        # Create variations of the name.
        variations = {entity, entity.upper()}
        # Add the aliases.
        variations |= aliases
        for variation in variations:
            # Add the variation if it's different from the base entity.
            if variation != entity:
                result.add(cls(variation, canonical_name=entity))
            # Add the determinant in different cases.
            for the in ['the', 'The', 'THE']:
                result.add(
                    cls(' '.join([the, variation]), canonical_name=entity)
                )
        return result


class Party(Entity):
    def __init__(self, name, canonical_name=None, member_of=None):
        super().__init__(name, canonical_name)
        self.member_of = member_of

    def __str__(self):
        s = self.name
        if self.name != self.canonical_name:
            s += f': {self.canonical_name}'
        if self.member_of is not None:
            s += f' [{", ".join(self.member_of)}]'
        return s

    @classmethod
    def load(cls, path):
        parties = list()
        for party, aliases, groupings in cls._parse(path):
            # Add the alias names in upper case.
            aliases |= {alias.upper() for alias in aliases}
            combinations = cls._combine(party, aliases)
            # Add the grouping to each party and add the party to the result.
            for party in combinations:
                if len(groupings) > 0:
                    party.member_of = groupings
                parties.append(party)
        return parties


class Grouping(Entity):
    def __init__(self, name, canonical_name=None):
        super().__init__(name, canonical_name)

    @classmethod
    def load(cls, path):
        groupings = list()
        for group, aliases, _ in cls._parse(path):
            # Add the group name in parenthesis after the aliases.
            aliases |= {' '.join([alias, f'({group})']) for alias in aliases}
            # Also when the alias name is in upper case but not the group name.
            aliases |= {
                ' '.join([alias.upper(), f'({group})']) for alias in aliases
            }
            combinations = cls._combine(group, aliases)
            groupings.extend(combinations)
        return groupings
