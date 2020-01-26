export function find_tag_by_key (tags, key, value) {
  for (let i in tags) {
    let tag = tags[i]
    if (tag[key] === value) {
      return tag
    }
  }
  return null
}

export function splice_bib_item_from_array (array_to_splice, key, value) {
  for (let i=0 ; i<array_to_splice.length ; i++) {
    if (array_to_splice[i][key] === value) {
      console.log(array_to_splice, key, value)
      array_to_splice.splice(i--, 1);
    }
  }
}
