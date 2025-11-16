class Page2Object {
  constructor(driver) {
    this.driver = driver;
  }

  async waitForPageLoad() {
    const titleElement = await this.driver.$('~page2Title');
    await titleElement.waitForDisplayed();
  }

  async isDataLoaded() {
    // Kontrola, zda se data načetla (buď prázdný stav nebo nějaká data)
    try {
      const emptyState = await this.driver.$('~list-empty-state');
      return await emptyState.isDisplayed();
    } catch {
      // Pokud není prázdný stav, zkusíme najít nějaký list item
      try {
        const firstItem = await this.driver.$('~list-item-1');
        return await firstItem.isDisplayed();
      } catch {
        return false;
      }
    }
  }

  async getListItemCount() {
    // Spočítá počet položek v seznamu
    const items = await this.driver.$$('[data-testid*="list-item-"]');
    return items.length;
  }

  async toggleItemCheckbox(itemId) {
    const checkbox = await this.driver.$(`~list-item-${itemId}-checkbox`);
    await checkbox.click();
  }

  async deleteItem(itemId) {
    const deleteButton = await this.driver.$(`~list-item-${itemId}-delete`);
    await deleteButton.click();
  }

  async refreshData() {
    const refreshButton = await this.driver.$('~refreshButton');
    await refreshButton.click();
  }

  async goBackToForm() {
    const backButton = await this.driver.$('~backButton');
    await backButton.click();
  }

  async isItemSelected(itemId) {
    // Kontrola, zda je položka vybraná (podle ikony checkboxu)
    // Toto by mohlo být složitější v závislosti na tom, jak je implementováno
    const checkbox = await this.driver.$(`~list-item-${itemId}-checkbox`);
    const iconName = await checkbox.getAttribute('name');
    return iconName === 'check-box'; // Předpokládáme, že vybraný checkbox má name 'check-box'
  }

  async clickOnName(itemId) {
    const nameElement = await this.driver.$(`~list-item-${itemId}-name`);
    await nameElement.click();
  }

  async isInfoModalVisible() {
    try {
      const modalContainer = await this.driver.$('~info-modal-container');
      return await modalContainer.isDisplayed();
    } catch {
      return false;
    }
  }

  async closeInfoModal() {
    const closeButton = await this.driver.$('~info-modal-close');
    await closeButton.click();
  }

  async confirmInfoModal() {
    const okButton = await this.driver.$('~info-modal-ok');
    await okButton.click();
  }

  async getInfoModalUserName() {
    // Získání jména z info modalu - může být složitější v závislosti na struktuře
    try {
      const modalContainer = await this.driver.$('~info-modal-container');
      const text = await modalContainer.getText();
      // Zde by bylo potřeba parsovat text nebo najít specifický element
      return text;
    } catch {
      return null;
    }
  }
}

export default Page2Object;