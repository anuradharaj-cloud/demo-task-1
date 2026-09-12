// =============================================================================
// Habot Connect FZCO - Hiring Project
// Position: Junior Cloud and Development Operations Engineer
// Candidate Full Name: Anuradha
// Candidate Electronic Mail Address: anuu.21092004@gmail.com
// File Purpose: Generate the submission slide deck. Maximum of fifteen slides.
// =============================================================================

const pptxgen = require("pptxgenjs");

const INK = "101A2B";
const NAVY = "1E2761";
const ICE = "CADCFC";
const PAPER = "F4F6F9";
const SLATE = "44566C";
const HALT = "C1272D";
const PASS = "1B7F5F";
const WHITE = "FFFFFF";

const HEAD_FONT = "Cambria";
const BODY_FONT = "Calibri";
const MONO_FONT = "Courier New";

const W = 13.33;
const H = 7.5;
const M = 0.62;

const presentation = new pptxgen();
presentation.layout = "LAYOUT_WIDE";
presentation.author = "Anuradha";
presentation.company = "Hiring project submission for Habot Connect FZCO";
presentation.title = "Deployment and Automation Blueprint";

function darkSlide() {
  const slide = presentation.addSlide();
  slide.background = { color: INK };
  return slide;
}

function lightSlide(titleText, kicker) {
  const slide = presentation.addSlide();
  slide.background = { color: PAPER };
  slide.addText(kicker.toUpperCase(), {
    x: M,
    y: 0.42,
    w: W - 2 * M,
    h: 0.26,
    fontFace: BODY_FONT,
    fontSize: 11,
    bold: true,
    color: SLATE,
    charSpacing: 2,
    isTextBox: true,
    margin: 0,
  });
  slide.addText(titleText, {
    x: M,
    y: 0.72,
    w: W - 2 * M,
    h: 0.72,
    fontFace: HEAD_FONT,
    fontSize: 32,
    bold: true,
    color: NAVY,
    isTextBox: true,
    margin: 0,
  });
  return slide;
}

function badge(slide, x, y, label, fill) {
  slide.addShape(presentation.ShapeType.ellipse, {
    x: x,
    y: y,
    w: 0.42,
    h: 0.42,
    fill: { color: fill },
  });
  slide.addText(label, {
    x: x,
    y: y,
    w: 0.42,
    h: 0.42,
    fontFace: BODY_FONT,
    fontSize: 13,
    bold: true,
    color: WHITE,
    align: "center",
    valign: "middle",
    isTextBox: true,
    margin: 0,
  });
}

function card(slide, options) {
  slide.addShape(presentation.ShapeType.roundRect, {
    x: options.x,
    y: options.y,
    w: options.w,
    h: options.h,
    rectRadius: 0.06,
    fill: { color: options.fill || WHITE },
    line: { color: options.line || "DDE3EA", width: 1 },
    shadow: {
      type: "outer",
      color: "9AA7B4",
      blur: 6,
      offset: 1,
      angle: 90,
      opacity: 0.22,
    },
  });
}

function tableOf(slide, headings, rows, options) {
  const headerRow = headings.map(function (text) {
    return {
      text: text,
      options: {
        bold: true,
        color: WHITE,
        fill: { color: NAVY },
        fontSize: options.headSize || 12,
      },
    };
  });
  const bodyRows = rows.map(function (row) {
    return row.map(function (cell) {
      if (typeof cell === "object") {
        return cell;
      }
      return { text: cell, options: { color: "22303F" } };
    });
  });
  slide.addTable([headerRow].concat(bodyRows), {
    x: options.x,
    y: options.y,
    w: options.w,
    colW: options.colW,
    fontFace: BODY_FONT,
    fontSize: options.fontSize || 11,
    border: { type: "solid", color: "DDE3EA", pt: 1 },
    fill: { color: WHITE },
    valign: "top",
    margin: 0.13,
  });
}

// ---------------------------------------------------------------- Slide 1 ---
(function () {
  const slide = darkSlide();
  slide.addText("Deployment and", {
    x: M,
    y: 1.45,
    w: 8.4,
    h: 0.78,
    fontFace: HEAD_FONT,
    fontSize: 46,
    bold: true,
    color: WHITE,
    isTextBox: true,
    margin: 0,
  });
  slide.addText("Automation Blueprint", {
    x: M,
    y: 2.18,
    w: 8.4,
    h: 0.78,
    fontFace: HEAD_FONT,
    fontSize: 46,
    bold: true,
    color: ICE,
    isTextBox: true,
    margin: 0,
  });
  slide.addText(
    "Secure staging provisioning, a fail closed build gate, and validation that removes human judgement.",
    {
      x: M,
      y: 3.14,
      w: 8.0,
      h: 0.7,
      fontFace: BODY_FONT,
      fontSize: 15,
      color: "9FB3C8",
      isTextBox: true,
      margin: 0,
    }
  );

  card(slide, {
    x: 9.3,
    y: 1.45,
    w: 3.4,
    h: 2.5,
    fill: "18263C",
    line: "2C405E",
  });
  slide.addText(
    [
      { text: "Anuradha\n", options: { bold: true, fontSize: 17, color: WHITE } },
      {
        text: "anuu.21092004@gmail.com\n\n",
        options: { fontSize: 12, color: ICE },
      },
      {
        text: "Junior Cloud and Development\nOperations Engineer\n\n",
        options: { fontSize: 12, color: "9FB3C8" },
      },
      {
        text: "Habot Connect FZCO, Dubai\nSeptember 2026",
        options: { fontSize: 12, color: "9FB3C8" },
      },
    ],
    {
      x: 9.55,
      y: 1.7,
      w: 2.9,
      h: 2.0,
      fontFace: BODY_FONT,
      isTextBox: true,
      margin: 0,
    }
  );

  const openingChips = [
    ["Task one", "Terraform secure staging\nprovisioning"],
    ["Task two", "A fail closed automated\nbuild gate"],
    ["Task three", "Schema mapping and yes or\nno validation"],
  ];
  let chipX = M;
  openingChips.forEach(function (chip) {
    card(slide, {
      x: chipX,
      y: 4.15,
      w: 3.82,
      h: 1.35,
      fill: "18263C",
      line: "2C405E",
    });
    slide.addText(chip[0].toUpperCase(), {
      x: chipX + 0.26,
      y: 4.36,
      w: 3.3,
      h: 0.26,
      fontFace: BODY_FONT,
      fontSize: 10,
      bold: true,
      color: "6E8299",
      charSpacing: 1.6,
      isTextBox: true,
      margin: 0,
    });
    slide.addText(chip[1], {
      x: chipX + 0.26,
      y: 4.66,
      w: 3.34,
      h: 0.7,
      fontFace: BODY_FONT,
      fontSize: 13,
      color: ICE,
      isTextBox: true,
      margin: 0,
    });
    chipX = chipX + 4.14;
  });

  slide.addText(
    "We do not rely on hope or human memory to prevent bugs. We build automated mistake proofing.",
    {
      x: M,
      y: 6.05,
      w: 11.0,
      h: 0.5,
      fontFace: HEAD_FONT,
      fontSize: 14,
      italic: true,
      color: "9FB3C8",
      isTextBox: true,
      margin: 0,
    }
  );
  slide.addNotes(
    "Introduce myself briefly. The deck is fifteen slides and the whole submission rests on one idea, which is on slide three."
  );
})();

// ---------------------------------------------------------------- Slide 2 ---
(function () {
  const slide = lightSlide("Two failures, one cause", "The incident");

  card(slide, { x: M, y: 1.72, w: 5.9, h: 1.92 });
  badge(slide, M + 0.3, 1.98, "1", HALT);
  slide.addText("A credential in plain text", {
    x: M + 0.88,
    y: 2.0,
    w: 4.8,
    h: 0.34,
    fontFace: BODY_FONT,
    fontSize: 16,
    bold: true,
    color: NAVY,
    isTextBox: true,
    margin: 0,
  });
  slide.addText(
    "An update bypassed the security guidelines and left unencrypted application programming interface credentials in raw application code.",
    {
      x: M + 0.3,
      y: 2.46,
      w: 5.3,
      h: 1.0,
      fontFace: BODY_FONT,
      fontSize: 13,
      color: SLATE,
      isTextBox: true,
      margin: 0,
    }
  );

  card(slide, { x: 6.82, y: 1.72, w: 5.9, h: 1.92 });
  badge(slide, 7.12, 1.98, "2", HALT);
  slide.addText("A schema mismatch", {
    x: 7.7,
    y: 2.0,
    w: 4.8,
    h: 0.34,
    fontFace: BODY_FONT,
    fontSize: 16,
    bold: true,
    color: NAVY,
    isTextBox: true,
    margin: 0,
  });
  slide.addText(
    "The same update changed the application model without changing the warehouse, and downstream analytics broke silently.",
    {
      x: 7.12,
      y: 2.46,
      w: 5.3,
      h: 1.0,
      fontFace: BODY_FONT,
      fontSize: 13,
      color: SLATE,
      isTextBox: true,
      margin: 0,
    }
  );

  card(slide, { x: M, y: 3.92, w: 12.1, h: 2.45, fill: "EEF2F7", line: "CBD6E2" });
  slide.addText("Both were possible for the same reason.", {
    x: M + 0.4,
    y: 4.2,
    w: 11.3,
    h: 0.42,
    fontFace: HEAD_FONT,
    fontSize: 22,
    bold: true,
    color: NAVY,
    isTextBox: true,
    margin: 0,
  });
  slide.addText(
    "A person was trusted to remember something. Remember not to paste the key. Remember to update the warehouse when you change the model.\n\nNeither is a knowledge problem, so neither is solved by training, documentation or a code review checklist. Every control in this submission replaces a thing a person must remember with a thing a machine refuses to allow.",
    {
      x: M + 0.4,
      y: 4.76,
      w: 11.3,
      h: 1.5,
      fontFace: BODY_FONT,
      fontSize: 13.5,
      color: "22303F",
      isTextBox: true,
      margin: 0,
    }
  );
  slide.addNotes(
    "The key sentence: neither failure is a knowledge problem, so neither is fixed by telling people to be careful."
  );
})();

// ---------------------------------------------------------------- Slide 3 ---
(function () {
  const slide = lightSlide("Remember, or refuse", "The principle");
  tableOf(
    slide,
    ["What a person had to remember", "What refuses it instead", "Where it lives"],
    [
      [
        "Do not commit a credential",
        "A secret scan of the full commit history that halts the build and quarantines the commit",
        { text: "Gate one", options: { color: SLATE } },
      ],
      [
        "Do not grant more access than needed",
        "Conditional bindings scoped to one object path, and a custom role granting exactly one permission",
        { text: "identity-and-access-management.tf", options: { color: SLATE } },
      ],
      [
        "Keep the serializer and the warehouse in step",
        "A consistency gate comparing them in four directions on every commit",
        { text: "Gate four", options: { color: SLATE } },
      ],
      [
        "Use the right field limits",
        "One field contract that the model, the serializer, the rule set and the workbook all read",
        { text: "field_contract.py", options: { color: SLATE } },
      ],
      [
        "Judge whether a submission is acceptable",
        "Seventy four rules, each answering a question whose only answers are yes and no",
        { text: "rules.py", options: { color: SLATE } },
      ],
      [
        "Run the formatter before pushing",
        "A formatting check that fails the build rather than reformatting quietly",
        { text: "Gates two and three", options: { color: SLATE } },
      ],
    ],
    { x: M, y: 1.78, w: 12.1, colW: [3.5, 5.8, 2.8], fontSize: 11.5 }
  );
  card(slide, { x: M, y: 5.62, w: 12.1, h: 1.28, fill: "EEF2F7", line: "CBD6E2" });
  slide.addText(
    "A rule is a Golden Rule only when breaking it is impossible, not when it is discouraged.",
    {
      x: M + 0.4,
      y: 5.86,
      w: 11.3,
      h: 0.36,
      fontFace: HEAD_FONT,
      fontSize: 17,
      bold: true,
      color: NAVY,
      isTextBox: true,
      margin: 0,
    }
  );
  slide.addText(
    "Anything held up by a code review, a checklist, a wiki page or an onboarding conversation is a recommendation. It works until somebody is tired, or new, or shipping at half past six on a Friday.",
    {
      x: M + 0.4,
      y: 6.28,
      w: 11.3,
      h: 0.5,
      fontFace: BODY_FONT,
      fontSize: 12.5,
      color: "22303F",
      isTextBox: true,
      margin: 0,
    }
  );
  slide.addNotes(
    "This table is the whole submission in one view. Everything after it is detail."
  );
})();

// ---------------------------------------------------------------- Slide 4 ---
(function () {
  const slide = lightSlide("One submission, five stages", "Architecture");

  const stages = [
    {
      title: "Application",
      detail:
        "Serializer fields built from the contract. An unknown field is refused, never dropped.",
    },
    {
      title: "D0 Raw Landing",
      detail:
        "Customer managed key. Public access prevented. Objects deleted after thirty days.",
    },
    {
      title: "Transformation",
      detail:
        "Runs the same validation library again, so the two answers cannot diverge.",
    },
    {
      title: "D1 Staged and Enforced",
      detail:
        "Partitioned and clustered. Native row access policy on the table.",
    },
    {
      title: "Reporting view",
      detail:
        "Authorised view only. The reader holds no permission on the table.",
    },
  ];

  let x = M;
  const cardWidth = 2.18;
  const gap = 0.3;
  stages.forEach(function (stage, index) {
    card(slide, { x: x, y: 1.95, w: cardWidth, h: 2.24 });
    badge(slide, x + 0.18, 2.12, String(index + 1), index === 1 ? NAVY : "5C7A99");
    slide.addText(stage.title, {
      x: x + 0.16,
      y: 2.66,
      w: cardWidth - 0.3,
      h: 0.58,
      fontFace: BODY_FONT,
      fontSize: 13,
      bold: true,
      color: NAVY,
      isTextBox: true,
      margin: 0,
    });
    slide.addText(stage.detail, {
      x: x + 0.16,
      y: 3.28,
      w: cardWidth - 0.28,
      h: 1.2,
      fontFace: BODY_FONT,
      fontSize: 10,
      valign: "top",
      color: SLATE,
      isTextBox: true,
      margin: 0,
    });
    if (index < stages.length - 1) {
      slide.addShape(presentation.ShapeType.rightArrow, {
        x: x + cardWidth + 0.02,
        y: 3.1,
        w: gap - 0.04,
        h: 0.2,
        fill: { color: "9AAABC" },
      });
    }
    x = x + cardWidth + gap;
  });

  card(slide, { x: M, y: 4.62, w: 12.1, h: 1.72, fill: "EEF2F7", line: "CBD6E2" });
  slide.addText(
    [
      {
        text: "The containment property.  ",
        options: { bold: true, color: NAVY, fontSize: 14 },
      },
      {
        text: "The ingestion identity can create an object and do nothing else. It cannot read what it wrote and it cannot list the bucket. If the web application is compromised tomorrow, the attacker gains the ability to add onboarding records. They gain no ability to read one existing family's data, and no ability to enumerate what is there.",
        options: { color: "22303F", fontSize: 13 },
      },
    ],
    {
      x: M + 0.4,
      y: 4.92,
      w: 11.3,
      h: 1.25,
      fontFace: BODY_FONT,
      isTextBox: true,
      margin: 0,
    }
  );
  slide.addNotes(
    "Walk left to right. Stop on the containment property, which is the reason the write only identity is worth the extra service account."
  );
})();

// ---------------------------------------------------------------- Slide 5 ---
(function () {
  const slide = lightSlide(
    "The estate, and why each control is there",
    "Task one. Infrastructure as code"
  );
  tableOf(
    slide,
    ["Control", "Setting", "The mistake it makes impossible"],
    [
      [
        "Uniform bucket level access",
        "true",
        "Removes per object access control lists, so no engineer can make one file public and never notice",
      ],
      [
        "Public access prevention",
        "enforced",
        "Enforced rather than inherited, so a policy change made elsewhere cannot open this bucket",
      ],
      [
        "Customer managed encryption",
        "Rotating every ninety days",
        "Habot Connect holds the key; rotation happens on a schedule nobody has to remember",
      ],
      [
        "Lifecycle deletion",
        "Thirty days",
        "Raw personal data of children is removed automatically once promoted, with no cleanup task to forget",
      ],
      [
        "Forced destruction",
        "Refused",
        "A populated bucket of children's data cannot be deleted by one command",
      ],
      [
        "Partition filter",
        "Required",
        "No query can scan the whole table by accident, which bounds both cost and exposure",
      ],
      [
        "Every variable",
        "Carries a validation rule",
        "A value that would produce an insecure estate is refused at plan time, before any call is made",
      ],
    ],
    { x: M, y: 1.78, w: 12.1, colW: [2.9, 2.5, 6.7], fontSize: 11 }
  );
  slide.addNotes(
    "If asked which single setting matters most: public access prevention set to enforced, because it survives changes made outside this configuration."
  );
})();

// ---------------------------------------------------------------- Slide 6 ---
(function () {
  const slide = lightSlide("Three identities, no overlap", "Task one. Least privilege");

  const identities = [
    {
      name: "onboarding-ingestion-writer",
      can: "Create an object beneath\nstudent-onboarding/",
      cannot: "Read any object.\nList the bucket.\nReach BigQuery at all.",
    },
    {
      name: "onboarding-transformation-runner",
      can: "Read that same path.\nAppend rows to the table.",
      cannot: "Delete data.\nChange the table schema.",
    },
    {
      name: "learning-support-analytics-reader",
      can: "Query the authorised view.",
      cannot: "Touch the underlying table.\nReach the landing bucket.",
    },
  ];

  let x = M;
  identities.forEach(function (identity) {
    card(slide, { x: x, y: 1.9, w: 3.82, h: 3.1 });
    slide.addText(identity.name, {
      x: x + 0.22,
      y: 2.12,
      w: 3.5,
      h: 0.5,
      fontFace: MONO_FONT,
      fontSize: 11,
      bold: true,
      color: NAVY,
      isTextBox: true,
      margin: 0,
    });
    slide.addText("CAN", {
      x: x + 0.22,
      y: 2.72,
      w: 3.5,
      h: 0.24,
      fontFace: BODY_FONT,
      fontSize: 10,
      bold: true,
      color: PASS,
      charSpacing: 1.5,
      isTextBox: true,
      margin: 0,
    });
    slide.addText(identity.can, {
      x: x + 0.22,
      y: 2.98,
      w: 3.5,
      h: 0.72,
      fontFace: BODY_FONT,
      fontSize: 11.5,
      color: "22303F",
      isTextBox: true,
      margin: 0,
    });
    slide.addText("CANNOT", {
      x: x + 0.22,
      y: 3.78,
      w: 3.5,
      h: 0.24,
      fontFace: BODY_FONT,
      fontSize: 10,
      bold: true,
      color: HALT,
      charSpacing: 1.5,
      isTextBox: true,
      margin: 0,
    });
    slide.addText(identity.cannot, {
      x: x + 0.22,
      y: 4.04,
      w: 3.5,
      h: 0.85,
      fontFace: BODY_FONT,
      fontSize: 11.5,
      color: "22303F",
      isTextBox: true,
      margin: 0,
    });
    x = x + 4.14;
  });

  slide.addText(
    "The predefined object creator role also permits listing the bucket, and an identity that can list the bucket can enumerate the families of other children. So the ingestion identity holds a custom role granting exactly one permission: storage.objects.create.",
    {
      x: M,
      y: 5.3,
      w: 12.1,
      h: 0.9,
      fontFace: BODY_FONT,
      fontSize: 13,
      color: SLATE,
      isTextBox: true,
      margin: 0,
    }
  );
  slide.addNotes(
    "The custom role is the detail worth defending. It is one extra resource and it removes the ability to enumerate personal data."
  );
})();

// ---------------------------------------------------------------- Slide 7 ---
(function () {
  const slide = lightSlide(
    "Row level security, built twice",
    "Task one. Data protection"
  );

  card(slide, { x: M, y: 1.85, w: 5.9, h: 2.55 });
  badge(slide, M + 0.28, 2.1, "1", NAVY);
  slide.addText("Native row access policy", {
    x: M + 0.86,
    y: 2.12,
    w: 4.8,
    h: 0.34,
    fontFace: BODY_FONT,
    fontSize: 16,
    bold: true,
    color: NAVY,
    isTextBox: true,
    margin: 0,
  });
  slide.addText(
    "Attached to the table, so it applies to every query, including one typed into a console.\n\nEntitlement is read from a table at query time, not from a permission somebody granted by hand. Revoking access is setting one boolean to false, with a review reference attached.",
    {
      x: M + 0.28,
      y: 2.56,
      w: 5.35,
      h: 1.6,
      fontFace: BODY_FONT,
      fontSize: 12.5,
      color: SLATE,
      isTextBox: true,
      margin: 0,
    }
  );

  card(slide, { x: 6.82, y: 1.85, w: 5.9, h: 2.55 });
  badge(slide, 7.1, 2.1, "2", NAVY);
  slide.addText("Authorised view", {
    x: 7.68,
    y: 2.12,
    w: 4.8,
    h: 0.34,
    fontFace: BODY_FONT,
    fontSize: 16,
    bold: true,
    color: NAVY,
    isTextBox: true,
    margin: 0,
  });
  slide.addText(
    "Authorising a view grants the view, not its readers, the right to read the table.\n\nThat is what lets the analytics identity hold no permission on the table at all. Direct identifiers of the child and of the parent never enter the view.",
    {
      x: 7.1,
      y: 2.56,
      w: 5.35,
      h: 1.6,
      fontFace: BODY_FONT,
      fontSize: 12.5,
      color: SLATE,
      isTextBox: true,
      margin: 0,
    }
  );

  card(slide, { x: M, y: 4.68, w: 12.1, h: 1.62, fill: "EEF2F7", line: "CBD6E2" });
  slide.addText("Why two layers rather than one", {
    x: M + 0.4,
    y: 4.92,
    w: 11.3,
    h: 0.35,
    fontFace: HEAD_FONT,
    fontSize: 18,
    bold: true,
    color: NAVY,
    isTextBox: true,
    margin: 0,
  });
  slide.addText(
    "A control that exists in one layer only is a control that one mistake removes. An engineer who deletes the row access policy still has the authorised view. An engineer who mistakenly grants the analytics identity direct table access still has the row access policy.",
    {
      x: M + 0.4,
      y: 5.36,
      w: 11.3,
      h: 0.8,
      fontFace: BODY_FONT,
      fontSize: 13,
      color: "22303F",
      isTextBox: true,
      margin: 0,
    }
  );
  slide.addNotes(
    "Expect a question on cost or complexity here. The answer is that the second layer costs one view and removes a single point of failure over children's data."
  );
})();

// ---------------------------------------------------------------- Slide 8 ---
(function () {
  const slide = lightSlide("The gate", "Task two. Fail closed pipeline");

  const gates = [
    {
      n: "1",
      title: "Secret detection and quarantine",
      body:
        "Full commit history, not the tip. Runs first, before anything can publish a log line or a cache entry derived from the code.",
    },
    {
      n: "2",
      title: "Infrastructure as code",
      body:
        "Format check, validate against the provider schema, lint, forbidden role assertion, public access assertion.",
    },
    {
      n: "3",
      title: "Application code",
      body:
        "Format check, import order, lint, security scan, fifty one tests, and an assertion that the suite is not empty.",
    },
    {
      n: "4",
      title: "Schema consistency",
      body:
        "The application field contract and the warehouse table compared in four directions.",
    },
  ];

  let y = 1.85;
  gates.forEach(function (gate) {
    card(slide, { x: M, y: y, w: 7.4, h: 1.0 });
    badge(slide, M + 0.24, y + 0.3, gate.n, NAVY);
    slide.addText(gate.title, {
      x: M + 0.84,
      y: y + 0.14,
      w: 6.3,
      h: 0.3,
      fontFace: BODY_FONT,
      fontSize: 14,
      bold: true,
      color: NAVY,
      isTextBox: true,
      margin: 0,
    });
    slide.addText(gate.body, {
      x: M + 0.84,
      y: y + 0.46,
      w: 6.4,
      h: 0.48,
      fontFace: BODY_FONT,
      fontSize: 10.5,
      color: SLATE,
      isTextBox: true,
      margin: 0,
    });
    y = y + 1.26;
  });

  card(slide, {
    x: 8.36,
    y: 1.85,
    w: 4.36,
    h: 2.4,
    fill: "1E2761",
    line: "1E2761",
  });
  slide.addText("Required status check", {
    x: 8.6,
    y: 2.08,
    w: 3.9,
    h: 0.32,
    fontFace: BODY_FONT,
    fontSize: 15,
    bold: true,
    color: WHITE,
    isTextBox: true,
    margin: 0,
  });
  slide.addText(
    "Branch protection requires this one job. It fails unless every gate reported the literal result success.\n\nCancelled, skipped and neutral are all failures to it.",
    {
      x: 8.6,
      y: 2.5,
      w: 3.9,
      h: 1.6,
      fontFace: BODY_FONT,
      fontSize: 12,
      color: ICE,
      isTextBox: true,
      margin: 0,
    }
  );

  card(slide, { x: 8.36, y: 4.45, w: 4.36, h: 1.95, fill: "F7E9E9", line: "E4C4C4" });
  slide.addText("No path around it", {
    x: 8.6,
    y: 4.68,
    w: 3.9,
    h: 0.3,
    fontFace: BODY_FONT,
    fontSize: 14,
    bold: true,
    color: HALT,
    isTextBox: true,
    margin: 0,
  });
  slide.addText(
    "Deployment sits behind the required check, the main branch, and a named human reviewer on the environment. A green build is evidence, not a decision.",
    {
      x: 8.6,
      y: 5.05,
      w: 3.9,
      h: 1.2,
      fontFace: BODY_FONT,
      fontSize: 11.5,
      color: "5A2A2A",
      isTextBox: true,
      margin: 0,
    }
  );
  slide.addNotes(
    "Mention that a pipeline which can be merged around is a recommendation, and that the branch protection document is half of this control."
  );
})();

// ---------------------------------------------------------------- Slide 9 ---
(function () {
  const slide = lightSlide(
    "Four structural rules make it fail closed",
    "Task two. How, not what"
  );
  tableOf(
    slide,
    ["Rule", "Why it is needed"],
    [
      [
        "The string continue-on-error appears nowhere in the workflow",
        "It is the single most common way a gate becomes a warning that everybody scrolls past",
      ],
      [
        "Every run step executes under bash with the options e, u and pipefail",
        "Without pipefail, a failing command inside a pipe is masked by the exit status of the last command in the pipe, so a linter appears to pass while having failed",
      ],
      [
        "Every dependent job declares an explicit success condition",
        "GitHub Actions skips a dependent job when its dependency fails, and a skipped job reports as neutral rather than as a failure",
      ],
      [
        "One required status check, carrying a completeness assertion",
        "It counts the gates that reported and requires the count to be four, so an engineer who adds a fifth gate without registering it is caught immediately",
      ],
    ],
    { x: M, y: 1.8, w: 12.1, colW: [4.5, 7.6], fontSize: 12 }
  );

  card(slide, { x: M, y: 5.25, w: 12.1, h: 1.15, fill: "EEF2F7", line: "CBD6E2" });
  slide.addText(
    "A reviewer can verify all four by reading the file, rather than by trusting me. That is deliberate: a control you have to take on trust is not a control.",
    {
      x: M + 0.4,
      y: 5.55,
      w: 11.3,
      h: 0.6,
      fontFace: BODY_FONT,
      fontSize: 13.5,
      color: "22303F",
      isTextBox: true,
      margin: 0,
    }
  );
  slide.addNotes(
    "The pipefail point is the one most candidates miss. Be ready to explain why a pipe masks a failure."
  );
})();

// --------------------------------------------------------------- Slide 10 ---
(function () {
  const slide = lightSlide(
    "Proof, not assertion",
    "Task two. The demonstration"
  );
  slide.addText(
    "One script runs the same checks the pipeline runs, twice: against the committed tree, then against a throwaway copy carrying a deliberately insecure commit. The output below is a real captured run, recorded in evidence/fail_closed_demonstration_transcript.txt.",
    {
      x: M,
      y: 1.66,
      w: 12.1,
      h: 0.64,
      fontFace: BODY_FONT,
      fontSize: 13,
      color: SLATE,
      isTextBox: true,
      margin: 0,
    }
  );

  tableOf(
    slide,
    ["Gate", "Clean tree", "Insecure commit"],
    [
      [
        "Secret detection and quarantine",
        { text: "PASS", options: { color: PASS, bold: true } },
        { text: "FAIL CLOSED — credential detected, build halted", options: { color: HALT, bold: true } },
      ],
      [
        "Python formatting",
        { text: "PASS", options: { color: PASS, bold: true } },
        { text: "FAIL CLOSED — source not in canonical format", options: { color: HALT, bold: true } },
      ],
      [
        "Python linting",
        { text: "PASS", options: { color: PASS, bold: true } },
        { text: "FAIL CLOSED — finding reported", options: { color: HALT, bold: true } },
      ],
      [
        "Schema consistency",
        { text: "PASS", options: { color: PASS, bold: true } },
        { text: "FAIL CLOSED — application and warehouse disagree", options: { color: HALT, bold: true } },
      ],
      [
        "Validation test suite, fifty one tests",
        { text: "PASS", options: { color: PASS, bold: true } },
        { text: "Not reached", options: { color: SLATE } },
      ],
    ],
    { x: M, y: 2.42, w: 12.1, colW: [4.1, 2.2, 5.8], fontSize: 10.5 }
  );

  card(slide, { x: M, y: 5.42, w: 12.1, h: 1.45, fill: "18263C", line: "18263C" });
  slide.addText(
    "The warehouse declares a column named parent_marketing_preference which is neither declared in the\nfield contract nor listed as a warehouse only column.",
    {
      x: M + 0.35,
      y: 5.66,
      w: 11.4,
      h: 0.6,
      fontFace: MONO_FONT,
      fontSize: 11,
      color: "A8D5C2",
      isTextBox: true,
      margin: 0,
    }
  );
  slide.addText(
    "The gate did not say that something looked wrong. It named the column, said which side declared it and which side did not, and said what to do.",
    {
      x: M + 0.35,
      y: 6.32,
      w: 11.4,
      h: 0.4,
      fontFace: BODY_FONT,
      fontSize: 12,
      italic: true,
      color: "9FB3C8",
      isTextBox: true,
      margin: 0,
    }
  );
  slide.addNotes(
    "Offer to run the script live. It takes a few seconds and needs no cloud account."
  );
})();

// --------------------------------------------------------------- Slide 11 ---
(function () {
  const slide = lightSlide(
    "One contract, four consumers",
    "Task three. Removing the second copy"
  );

  card(slide, { x: 4.55, y: 1.85, w: 4.2, h: 1.15, fill: "1E2761", line: "1E2761" });
  slide.addText("field_contract.py", {
    x: 4.7,
    y: 2.06,
    w: 3.9,
    h: 0.32,
    fontFace: MONO_FONT,
    fontSize: 14,
    bold: true,
    color: WHITE,
    align: "center",
    isTextBox: true,
    margin: 0,
  });
  slide.addText("Every limit, stated once", {
    x: 4.7,
    y: 2.46,
    w: 3.9,
    h: 0.3,
    fontFace: BODY_FONT,
    fontSize: 12,
    color: ICE,
    align: "center",
    isTextBox: true,
    margin: 0,
  });

  const consumers = [
    ["Django model", "Maximum lengths, numeric\nbounds and patterns become\ndatabase constraints"],
    ["REST serializer", "Fields are built from the\ncontract, so no limit is\ntyped into the serializer"],
    ["Validation library", "Per field rules are generated,\nso a field added to the\ncontract is a field with rules"],
    ["Mapping workbook", "Generated, never typed, so\nthe document cannot describe\na field that does not exist"],
  ];

  const consumerCardWidth = 2.8;
  const consumerCardStep = 3.1;
  const firstConsumerCentre = M + consumerCardWidth / 2;
  const lastConsumerCentre = firstConsumerCentre + consumerCardStep * 3;

  // A single trunk from the contract box down to a horizontal rail, then one
  // short riser into each consumer card. Drawn as three kinds of straight line
  // so that nothing terminates in mid air.
  slide.addShape(presentation.ShapeType.line, {
    x: 6.65,
    y: 3.0,
    w: 0,
    h: 0.36,
    line: { color: "AEBCCB", width: 1.5 },
  });
  slide.addShape(presentation.ShapeType.line, {
    x: firstConsumerCentre,
    y: 3.36,
    w: lastConsumerCentre - firstConsumerCentre,
    h: 0,
    line: { color: "AEBCCB", width: 1.5 },
  });

  let x = M;
  consumers.forEach(function (consumer, consumerIndex) {
    slide.addShape(presentation.ShapeType.line, {
      x: firstConsumerCentre + consumerCardStep * consumerIndex,
      y: 3.36,
      w: 0,
      h: 0.36,
      line: { color: "AEBCCB", width: 1.5 },
    });
    card(slide, { x: x, y: 3.72, w: consumerCardWidth, h: 1.95 });
    slide.addText(consumer[0], {
      x: x + 0.2,
      y: 3.95,
      w: 2.45,
      h: 0.32,
      fontFace: BODY_FONT,
      fontSize: 13.5,
      bold: true,
      color: NAVY,
      isTextBox: true,
      margin: 0,
    });
    slide.addText(consumer[1], {
      x: x + 0.2,
      y: 4.35,
      w: 2.46,
      h: 1.15,
      fontFace: BODY_FONT,
      fontSize: 10.5,
      color: SLATE,
      isTextBox: true,
      margin: 0,
    });
    x = x + consumerCardStep;
  });

  slide.addText(
    "An engineer cannot widen a limit in one place, because there is no second place to widen. The fifth consumer is the schema consistency gate, which compares the contract against the warehouse on every commit.",
    {
      x: M,
      y: 5.9,
      w: 12.1,
      h: 0.75,
      fontFace: BODY_FONT,
      fontSize: 13,
      color: "22303F",
      isTextBox: true,
      margin: 0,
    }
  );
  slide.addNotes(
    "This slide is the answer to the schema mismatch half of the incident."
  );
})();

// --------------------------------------------------------------- Slide 12 ---
(function () {
  const slide = lightSlide(
    "Seventy four questions, no opinions",
    "Task three. The validation library"
  );

  const stats = [
    ["74", "rules applied to every\nsubmission"],
    ["2", "possible answers per rule:\nyes and no"],
    ["0", "thresholds, weightings\nor overrides"],
  ];
  let x = M;
  stats.forEach(function (stat) {
    card(slide, { x: x, y: 1.85, w: 3.82, h: 1.55 });
    slide.addText(stat[0], {
      x: x + 0.22,
      y: 1.98,
      w: 1.2,
      h: 0.85,
      fontFace: HEAD_FONT,
      fontSize: 44,
      bold: true,
      color: NAVY,
      isTextBox: true,
      margin: 0,
    });
    slide.addText(stat[1], {
      x: x + 1.45,
      y: 2.16,
      w: 2.3,
      h: 0.95,
      fontFace: BODY_FONT,
      fontSize: 11.5,
      color: SLATE,
      isTextBox: true,
      margin: 0,
    });
    x = x + 4.14;
  });

  tableOf(
    slide,
    ["A rule from the register", "The judgement it replaces"],
    [
      [
        "Is the education, health and care plan reference present exactly when the payload states that a plan is held?",
        "A reviewer deciding whether a missing reference is acceptable this once",
      ],
      [
        "Is the stated year group within one of the year group implied by the date of birth?",
        "A reviewer deciding whether a stated year group looks plausible",
      ],
      [
        "Is every field in the payload one of the fields declared in the field contract?",
        "A framework quietly discarding a key the client believed it had sent",
      ],
      [
        "Has the parent or guardian given explicit consent to processing?",
        "Nothing. This one is enforced twice, in the serializer and as a database check constraint",
      ],
    ],
    { x: M, y: 3.74, w: 12.1, colW: [7.1, 5.0], fontSize: 11.5 }
  );

  slide.addText(
    "A rule that raises an exception is recorded as no, never allowed to escape. An exception escaping the validator would either halt ingestion or, far worse, be caught upstream and treated as a pass.",
    {
      x: M,
      y: 6.45,
      w: 12.1,
      h: 0.55,
      fontFace: BODY_FONT,
      fontSize: 12.5,
      italic: true,
      color: SLATE,
      isTextBox: true,
      margin: 0,
    }
  );
  slide.addNotes(
    "Every answer is written into the warehouse beside the row, so any acceptance can be reconstructed years later."
  );
})();

// --------------------------------------------------------------- Slide 13 ---
(function () {
  const slide = lightSlide(
    "Why the same code runs twice",
    "Task three. The boundary"
  );

  card(slide, { x: M, y: 1.9, w: 3.82, h: 2.5, fill: "F7E9E9", line: "E4C4C4" });
  slide.addText("Validate only at the application", {
    x: M + 0.22,
    y: 2.12,
    w: 3.4,
    h: 0.6,
    fontFace: BODY_FONT,
    fontSize: 14,
    bold: true,
    color: HALT,
    isTextBox: true,
    margin: 0,
  });
  slide.addText(
    "A payload arriving by any other route reaches the warehouse unvalidated: a backfill, a migration, a manual load, a second service written next year.",
    {
      x: M + 0.22,
      y: 2.62,
      w: 3.42,
      h: 1.55,
      fontFace: BODY_FONT,
      fontSize: 11.5,
      color: "5A2A2A",
      isTextBox: true,
      margin: 0,
    }
  );

  card(slide, { x: 4.76, y: 1.9, w: 3.82, h: 2.5, fill: "F7E9E9", line: "E4C4C4" });
  slide.addText("Validate only at load", {
    x: 4.98,
    y: 2.12,
    w: 3.4,
    h: 0.6,
    fontFace: BODY_FONT,
    fontSize: 14,
    bold: true,
    color: HALT,
    isTextBox: true,
    margin: 0,
  });
  slide.addText(
    "The parent gets no immediate feedback, and a bad submission occupies the raw landing bucket until somebody investigates it.",
    {
      x: 4.98,
      y: 2.62,
      w: 3.42,
      h: 1.4,
      fontFace: BODY_FONT,
      fontSize: 11.5,
      color: "5A2A2A",
      isTextBox: true,
      margin: 0,
    }
  );

  card(slide, { x: 8.9, y: 1.9, w: 3.82, h: 2.5, fill: "E6F2EC", line: "BBD9CB" });
  slide.addText("Run the same code at both", {
    x: 9.12,
    y: 2.12,
    w: 3.4,
    h: 0.6,
    fontFace: BODY_FONT,
    fontSize: 14,
    bold: true,
    color: PASS,
    isTextBox: true,
    margin: 0,
  });
  slide.addText(
    "Immediate feedback for the parent, and a boundary nothing can route around. The important word is same: two implementations of the same rules drift, and the drift is silent.",
    {
      x: 9.12,
      y: 2.62,
      w: 3.42,
      h: 1.5,
      fontFace: BODY_FONT,
      fontSize: 11.5,
      color: "1F4A3B",
      isTextBox: true,
      margin: 0,
    }
  );

  card(slide, { x: M, y: 4.75, w: 12.1, h: 1.7, fill: "EEF2F7", line: "CBD6E2" });
  slide.addText("Verify every claim in this submission in under a minute", {
    x: M + 0.4,
    y: 4.98,
    w: 11.3,
    h: 0.35,
    fontFace: HEAD_FONT,
    fontSize: 18,
    bold: true,
    color: NAVY,
    isTextBox: true,
    margin: 0,
  });
  slide.addText(
    "python3 -m pytest                                        →  51 passed\npython3 scripts/assert_schema_consistency.py             →  the schemas agree\nbash quarantine-demonstration/run_fail_closed_demonstration.sh   →  DEMONSTRATION SUCCEEDED",
    {
      x: M + 0.4,
      y: 5.42,
      w: 11.3,
      h: 0.9,
      fontFace: MONO_FONT,
      fontSize: 10.5,
      color: "22303F",
      isTextBox: true,
      margin: 0,
    }
  );
  slide.addNotes("No Google Cloud account and no billing account are needed for any of these.");
})();

// --------------------------------------------------------------- Slide 14 ---
(function () {
  const slide = lightSlide(
    "What this does not do",
    "Honest limits"
  );
  slide.addText(
    "Stating the boundary of a piece of work matters more than claiming completeness. A demonstration that claims more than it shows is the same species of problem as a linter that warns and continues.",
    {
      x: M,
      y: 1.66,
      w: 12.1,
      h: 0.6,
      fontFace: BODY_FONT,
      fontSize: 13,
      color: SLATE,
      isTextBox: true,
      margin: 0,
    }
  );
  tableOf(
    slide,
    ["Not covered", "What would close it"],
    [
      [
        "No scan for vulnerable dependencies. Versions are pinned exactly, which makes the build reproducible but not current",
        "Dependabot or an equivalent, plus a gate on known vulnerabilities with a defined severity threshold",
      ],
      [
        "No policy engine over the Terraform plan. The assertions in gate two are targeted searches that catch the named mistakes and nothing else",
        "Open Policy Agent or Checkov, evaluating the plan output rather than the source text",
      ],
      [
        "The Terraform is validated, not exercised. Validation proves the configuration is correct against the provider schema, not that the estate behaves as intended",
        "Terratest against a throwaway project, asserting that the write only identity genuinely cannot read",
      ],
      [
        "The row access policy is applied by a job rather than by a first class resource",
        "A dedicated resource once it is available, keeping the statement in version control either way",
      ],
    ],
    { x: M, y: 2.4, w: 12.1, colW: [6.6, 5.5], fontSize: 11.5 }
  );
  card(slide, { x: M, y: 5.72, w: 12.1, h: 1.18, fill: "EEF2F7", line: "CBD6E2" });
  slide.addText(
    "Each of these is a deliberate scope decision for a four to six hour project, not an oversight. I would rather name the boundary than let a reviewer discover it.",
    {
      x: M + 0.4,
      y: 6.06,
      w: 11.3,
      h: 0.55,
      fontFace: BODY_FONT,
      fontSize: 13.5,
      color: "22303F",
      isTextBox: true,
      margin: 0,
    }
  );
  slide.addNotes(
    "Volunteer this slide rather than waiting to be asked. Each item is a scope decision for a four to six hour project, not an oversight."
  );
})();

// --------------------------------------------------------------- Slide 15 ---
(function () {
  const slide = darkSlide();
  slide.addText("The one sentence", {
    x: M,
    y: 1.5,
    w: 11.0,
    h: 0.4,
    fontFace: BODY_FONT,
    fontSize: 12,
    bold: true,
    color: "6E8299",
    charSpacing: 2,
    isTextBox: true,
    margin: 0,
  });
  slide.addText(
    "Every control here replaces something a person\nhad to remember with something a machine refuses.",
    {
      x: M,
      y: 2.05,
      w: 11.6,
      h: 1.5,
      fontFace: HEAD_FONT,
      fontSize: 33,
      bold: true,
      color: WHITE,
      isTextBox: true,
      margin: 0,
    }
  );
  slide.addText(
    "That is the only design principle used in this submission. The Terraform, the pipeline and the validation library are three applications of it.",
    {
      x: M,
      y: 3.65,
      w: 10.6,
      h: 0.6,
      fontFace: BODY_FONT,
      fontSize: 14,
      color: "9FB3C8",
      isTextBox: true,
      margin: 0,
    }
  );

  card(slide, { x: M, y: 4.7, w: 5.9, h: 1.8, fill: "18263C", line: "2C405E" });
  slide.addText("Thank you", {
    x: M + 0.35,
    y: 4.95,
    w: 5.2,
    h: 0.38,
    fontFace: HEAD_FONT,
    fontSize: 20,
    bold: true,
    color: ICE,
    isTextBox: true,
    margin: 0,
  });
  slide.addText(
    "Anuradha\nanuu.21092004@gmail.com\nJunior Cloud and Development Operations Engineer",
    {
      x: M + 0.35,
      y: 5.4,
      w: 5.2,
      h: 0.95,
      fontFace: BODY_FONT,
      fontSize: 11.5,
      color: "9FB3C8",
      isTextBox: true,
      margin: 0,
    }
  );

  card(slide, { x: 6.82, y: 4.7, w: 5.9, h: 1.8, fill: "18263C", line: "2C405E" });
  slide.addText("In the repository", {
    x: 7.17,
    y: 4.95,
    w: 5.2,
    h: 0.38,
    fontFace: HEAD_FONT,
    fontSize: 20,
    bold: true,
    color: ICE,
    isTextBox: true,
    margin: 0,
  });
  slide.addText(
    "README.md\ndocs/GOLDEN_RULES_AND_POKA_YOKE_DESIGN.md\nevidence/fail_closed_demonstration_transcript.txt\nschema-mapping/student_onboarding_schema_mapping.xlsx",
    {
      x: 7.17,
      y: 5.38,
      w: 5.3,
      h: 1.05,
      fontFace: BODY_FONT,
      fontSize: 10.5,
      color: "9FB3C8",
      lineSpacingMultiple: 1.12,
      isTextBox: true,
      margin: 0,
    }
  );
  slide.addNotes(
    "Close on the one sentence, then invite questions. Offer to run the fail closed demonstration live."
  );
})();

presentation
  .writeFile({
    fileName:
      "/home/claude/habot-connect-hiring-project/presentation/" +
      "Anuradha-Habot-Connect-Hiring-Project.pptx",
  })
  .then(function (fileName) {
    console.log("Written: " + fileName);
  });
