export function find_tag_by_key (tags, key, value) {
  for (let i in tags) {
    let tag = tags[i]
    if (tag[key] === value) {
      return tag
    }
  }
  throw new Error(`Couldn't find a tag with '${key}'='${value}'`);
}