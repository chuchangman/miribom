let savedSearchState = null

export const useProductSearchState = () => {
  const saveSearchState = ({
    routeKey,
    products,
    nextOffset,
    hasNext,
    scrollY,
  }) => {
    savedSearchState = {
      routeKey,
      products,
      nextOffset,
      hasNext,
      scrollY,
    }
  }

  const restoreSearchState = (routeKey) => {
    if (savedSearchState?.routeKey !== routeKey) {
      return null
    }

    return {
      products: savedSearchState.products,
      nextOffset: savedSearchState.nextOffset,
      hasNext: savedSearchState.hasNext,
      scrollY: savedSearchState.scrollY,
    }
  }

  const clearSearchState = () => {
    savedSearchState = null
  }

  return {
    saveSearchState,
    restoreSearchState,
    clearSearchState,
  }
}
