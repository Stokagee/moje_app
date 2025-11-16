class FormPageObject {
  constructor(driver) {
    this.driver = driver;
  }

  async enterFirstName(firstName) {
    const element = await this.driver.$('~firstNameInput');
    await element.setValue(firstName);
  }

  async enterLastName(lastName) {
    const element = await this.driver.$('~lastNameInput');
    await element.setValue(lastName);
  }

  async enterPhone(phone) {
    const element = await this.driver.$('~phoneInput');
    await element.setValue(phone);
  }

  async selectGender(gender) {
    const element = await this.driver.$('~genderPicker');
    await element.click();
    
    // Počkej na modal a vyber hodnotu pomocí testID
    const genderOption = await this.driver.$(`~gender-option-${gender}`);
    await genderOption.click();
  }

  async submitForm() {
    const element = await this.driver.$('~submitButton');
    await element.click();
  }

  async isFormSubmitted() {
    // Kontrola úspěšného odeslání - čekání na modal s úspěchem
    const successModal = await this.driver.$('~formSuccessModal');
    return await successModal.waitForDisplayed({ timeout: 5000 });
  }
}

export default FormPageObject;